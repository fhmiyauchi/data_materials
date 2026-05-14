import os
from src.ai.llm_chain import AIWorkflow
import json

workflow = AIWorkflow()
query = "Looking for a non-metallic material with a very wide band gap"
explanation, candidates, intent = workflow.process_query(query)

print("\n--- RAW EXPLANATION TEXT ---")
print(repr(candidates[0]['explanation']))
print("----------------------------\n")
