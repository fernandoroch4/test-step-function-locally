import json
import glob
import boto3


def get_asl_files() -> list:
    files = glob.glob("**/*.asl.json", recursive=True) 
    return files

def get_mock_file() -> list:
    files = glob.glob("**/MockConfigFile.json", recursive=True) 
    return files

class StepFunctionLocally:
    def __init__(self, environment="pipe"):
        if environment == "pipe":
            self.endpoint = "http://0.0.0.0:8083"
        else:
            self.endpoint = "http://localhost:8083"

        self.sfn = boto3.client("stepfunctions", endpoint_url=self.endpoint)


if __name__ == "__main__":
    errors = []

    asl_files = get_asl_files()
    mock_files = get_mock_file()
    if len(asl_files) == 0: errors.append("No ASL files found")
    if len(mock_files) == 0: errors.append("No Mock file found")
    if len(mock_files) > 1: errors.append("More than one Mock file found")

    assertions = json.loads(open(mock_files[0]).read()).get("Assert", {})
    if len(assertions) == 0: errors.append("No assertions found inside MockConfigFile")
    
    states = []
    for asl_file in asl_files:
        state_machine_name = asl_file.split("/")[-1].split(".")[0] # based on asl file
        state_machine_tests = assertions.get(state_machine_name, []),
        if len(state_machine_tests[0]) == 0:
            errors.append(f"No assertions found for state machine {state_machine_name}")

        states.append({
            "Name": state_machine_name,
            "Tests": state_machine_tests
        })

    if len(errors) > 0:
        print("ASL files:")
        print(json.dumps(asl_files, indent=2))
        print("Mock files:")
        print(json.dumps(mock_files, indent=2))
        print("Errors:")
        print(json.dumps(errors, indent=2))
        print("Exiting...")
        exit(1)
    
    # StepFunctionLocally = StepFunctionLocally(environment="local")