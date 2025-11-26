import sys
from src.orchestrator.pipeline import run_pipeline

def main():
    if len(sys.argv) < 2:
        query = "Analyze ROAS drop in last 7 days"
    else:
        query = sys.argv[1]

    result = run_pipeline(query=query)
    print("Pipeline completed.")
    print("Report:", result["paths"]["report"])
    print("Insights JSON:", result["paths"]["insights"])
    print("Creatives JSON:", result["paths"]["creatives"])

if __name__ == "__main__":
    main()
