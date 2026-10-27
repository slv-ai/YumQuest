import sys
from rag import answer_query, save_feedback

question = " ".join(sys.argv[1:])
if not question:
    raise SystemExit('Usage: python ask.py "your question"')

r = answer_query(question)
print("\n" + r["answer"] + "\n")
print("Recipes used:")
for id, title, _, _, _ in r["recipes"]:
    print(f"  - {title}")
print(f"\n[{r['model']} | {r['prompt_tokens']}+{r['response_tokens']} tokens | "
    f"${r['cost']:.5f} | {r['seconds']:.1f}s | saved as conversation #{r['id']}]")

rating = input("\nHelpful? (y = yes, n = no, Enter = skip): ").strip().lower()
if rating in ("y", "n"):
    save_feedback(r["id"], 1 if rating == "y" else -1)
    print("Feedback saved.")