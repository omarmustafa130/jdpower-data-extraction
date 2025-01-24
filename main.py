import subprocess
import sys

def setup_environment():
    """Install necessary libraries and set up the environment."""
    print("Setting up the environment...")
    try:
        subprocess.check_call([sys.executable, "setup.py"])
    except FileNotFoundError:
        print("Error: `setup.py` not found. Ensure the setup script exists in the same directory.")
    except Exception as e:
        print(f"Error during setup: {e}")

def run_script(script_name, *args):
    """Run a specific script with optional arguments."""
    try:
        print(f"Running {script_name}...")
        command = [sys.executable, script_name] + list(args)
        subprocess.check_call(command)
    except FileNotFoundError:
        print(f"Error: `{script_name}` not found. Ensure the script exists in the same directory.")
    except Exception as e:
        print(f"Error while running {script_name}: {e}")

def ask_vehicle_types():
    """Prompt user to select vehicle types."""
    print("\nWhich vehicle types would you like to process?")
    print("-c: Cars")
    print("-all: All vehicle types")
    return input("Enter your choice (-c, -r, -m, -b, -all): ")

def main():
    while True:
        print("\nChoose an option:")
        print("1. Generate initial dataset (makes and years only)")
        print("2. Generate full dataset without reviews")
        print("3. Generate full dataset with reviews")
        print("4. Generate reviews only")  
        print("5. Setup environment")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            run_script("generate_initial_dataset.py")
        elif choice == "2":
            year_input = input("Enter the year or range of years (e.g., 2025 or 2023-2025): ")
            vehicle_choice = ask_vehicle_types()
            if vehicle_choice in ["-c", "-r", '-m', '-b', "-all"]:
                # Split the vehicle_choice into individual flags
                flags = []
                if "-c" in vehicle_choice or vehicle_choice == "-all":
                    flags.append("-c")
                if "-r" in vehicle_choice or vehicle_choice == "-all":
                    flags.append("-r")
                if "-b" in vehicle_choice or vehicle_choice == "-all":
                    flags.append("-b")
                if "-m" in vehicle_choice or vehicle_choice == "-all":
                    flags.append("-m")
                # Run the script with the individual flags
                run_script("generate_full_dataset.py", "--years", year_input, *flags)
            else:
                print("Invalid choice. Skipping dataset generation.")
        elif choice == "3":
            year_input = input("Enter the year or range of years (e.g., 2025 or 2023-2025): ")
            vehicle_choice = ask_vehicle_types()
            if vehicle_choice in ["-c", "-r", '-m', '-b', "-all"]:
                # Split the vehicle_choice into individual flags
                flags = []
                if "-c" in vehicle_choice or vehicle_choice == "-all":
                    flags.append("-c")
                if "-r" in vehicle_choice or vehicle_choice == "-all":
                    flags.append("-r")
                if "-b" in vehicle_choice or vehicle_choice == "-all":
                    flags.append("-b")
                if "-m" in vehicle_choice or vehicle_choice == "-all":
                    flags.append("-m")
                # Run the script with the individual flags
                run_script("generate_full_dataset.py", "--years", year_input, *flags)
                run_script("generate_reviews.py", vehicle_choice)
            else:
                print("Invalid choice. Skipping dataset generation.")
        elif choice == "4":  # New option to generate reviews only
            review_choice = ask_vehicle_types()
            if vehicle_choice in ["-c", "-r", '-m', '-b', "-all"]:
                # Split the review_choice into individual flags
                flags = []
                if "-c" in review_choice or review_choice == "-all":
                    flags.append("-c")
                if "-r" in review_choice or review_choice == "-all":
                    flags.append("-r")
                if "-b" in review_choice or review_choice == "-all":
                    flags.append("-b")
                if "-m" in review_choice or review_choice == "-all":
                    flags.append("-m")
                # Run the script with the individual flags
                run_script("generate_reviews.py", *flags)
            else:
                print("Invalid choice. Skipping review generation.")
        elif choice == "5":
            setup_environment()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main()
