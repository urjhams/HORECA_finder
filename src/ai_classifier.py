"""
AI Classifier Module
"""

import json
import time
import os
from typing import List, Dict, Callable
try:
    from src.utils import FileManager
except ImportError:
    from utils import FileManager

class AIClassifier:
    """Classify leads using LLM (OpenAI or similar)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.call_count = 0

    def classify_batch(self, records: List[Dict], prompt_generator: Callable[[List[Dict]], str]) -> List[Dict]:
        """Classify a batch of records using LLM"""
        
        if not self.api_key:
            print("⚠️  No OpenAI API key configured. Skipping batch.")
            return [{}] * len(records)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            prompt = prompt_generator(records)

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business analyst. Always return a valid JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )

            result_text = response.choices[0].message.content.strip()
            # Clean up potential markdown code blocks
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            results_list = json.loads(result_text)
            
            self.call_count += 1
            return results_list

        except Exception as e:
            print(f"    ❌ Batch classification error: {str(e)}")
            # Return empty dicts for failed batch to maintain length alignment
            return [{}] * len(records)

    def classify_all(self, records: List[Dict], prompt_generator: Callable[[List[Dict]], str], 
                     output_file: str, batch_size: int = 10, resume: bool = True) -> List[Dict]:
        """Classify all records with resume capability, incremental saving, and batch processing"""

        print("\n" + "="*70)
        print("PHASE 3: AI CLASSIFICATION (BATCH MODE)")
        print("="*70)

        # Load existing progress if available
        classified_leads = []
        processed_ids = set()
        
        # Check if we have an existing classified file to resume from
        if resume and os.path.exists(output_file):
            print(f"📂 Found existing classified leads file: {output_file}")
            classified_leads = FileManager.load_csv(output_file)
            for r in classified_leads:
                # Use ID if available, otherwise fallback to name+city
                uid = r.get("id") or f"{r.get('company_name')}_{r.get('city')}"
                processed_ids.add(uid)
            print(f"⏩ Skipping {len(classified_leads)} already classified records.")

        # Identify remaining records
        remaining_records = []
        for r in records:
            uid = r.get("id") or f"{r.get('company_name')}_{r.get('city')}"
            if uid not in processed_ids:
                remaining_records.append(r)

        if not remaining_records:
            print("✅ All records already classified!")
            return classified_leads

        print(f"📊 Remaining to classify: {len(remaining_records)}")
        print(f"📦 Batch size: {batch_size}")

        # Process remaining records in batches
        total_batches = (len(remaining_records) + batch_size - 1) // batch_size
        
        for i in range(0, len(remaining_records), batch_size):
            batch_num = (i // batch_size) + 1
            batch_records = remaining_records[i : i + batch_size]
            
            print(f"\n  Processing Batch {batch_num}/{total_batches} ({len(batch_records)} records)...", end=" ", flush=True)
            
            # Call LLM
            batch_results = self.classify_batch(batch_records, prompt_generator)
            
            # Merge results back to records
            success_count = 0
            for j, record in enumerate(batch_records):
                # Try to find matching result by index or order
                # Since we asked for record_index, we can try to use it, but fallback to order
                res = {}
                if j < len(batch_results):
                    res = batch_results[j]
                
                if res:
                    record.update(res)
                    success_count += 1
                else:
                    record["contact_recommendation"] = "Error/Skipped in batch"
                
                classified_leads.append(record)

            print(f"✅ {success_count}/{len(batch_records)} classified")

            # Incremental save after every batch
            print(f"    💾 Saving progress ({len(classified_leads)} total)...")
            FileManager.save_csv(classified_leads, output_file)

            # Rate limit: 3-4 requests per minute (approx 15-20s delay)
            time.sleep(10)

        print(f"\n✅ Total batch calls: {self.call_count}")
        
        return classified_leads
