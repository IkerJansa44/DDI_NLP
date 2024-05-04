import subprocess

i=0
while i <= 1:
    # Command to run the model
    model_command = ["python", "predict-sklearn.py", "model.joblib", "vectorizer.joblib", str(i)]

    # Command to evaluate results
    evaluate_command = ["python", "evaluator.py", "DDI", "./data/devel/", "devel.out"]

    print("Running model...")
    subprocess.run(model_command, stdin=open("devel.cod", "r"), stdout=open("devel.out", "w"), check=True)

    print("Evaluating results...")
    subprocess.run(evaluate_command, stdout=open("devel.stats", "w"), check=True)

    i += 0.05