# additional.pyw - Test script for GitHub Launcher
import time
import random
import sys
import datetime

def main():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ✅ Additional script started!")
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🚀 Running random operations...")
    
    # Seed random with current time
    random.seed(time.time())
    
    counter = 0
    try:
        while True:
            counter += 1
            
            # Generate random activity
            activity = random.choice([
                "Generating random number...",
                "Calculating Pi approximation...",
                "Simulating CPU load...",
                "Checking system time...",
                "Performing memory test...",
                "Running diagnostics...",
                "Processing data...",
                "Updating cache...",
                "Validating input...",
                "Optimizing performance..."
            ])
            
            # Random number operations
            num1 = random.randint(1, 100)
            num2 = random.randint(1, 100)
            operation = random.choice(['+', '-', '*', '/'])
            
            if operation == '+':
                result = num1 + num2
                operation_str = f"{num1} + {num2}"
            elif operation == '-':
                result = num1 - num2
                operation_str = f"{num1} - {num2}"
            elif operation == '*':
                result = num1 * num2
                operation_str = f"{num1} × {num2}"
            else:  # division
                if num2 != 0:
                    result = num1 / num2
                    operation_str = f"{num1} ÷ {num2}"
                else:
                    result = "undefined"
                    operation_str = f"{num1} ÷ {num2}"
            
            # Random status message
            status = random.choice([
                "✅ Success",
                "⚠️ Warning",
                "ℹ️ Info",
                "🔧 Processing",
                "📊 Analyzing",
                "🔍 Monitoring",
                "⚡ Optimizing",
                "🔄 Refreshing",
                "🔐 Securing",
                "📈 Reporting"
            ])
            
            # Print the activity
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [{status}] {activity}")
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🧮 Calculation: {operation_str} = {result}")
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 📊 Iteration: {counter}, Memory Usage: {random.randint(10, 90)}%")
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ⏱️ Uptime: {counter * 10} seconds")
            print("-" * 50)
            
            # Random sleep between 5 and 15 seconds
            sleep_time = random.randint(5, 15)
            time.sleep(sleep_time)
            
            # Random chance to simulate an error (1 in 20 iterations)
            if random.random() < 0.05:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ⚠️ Simulated warning: Random warning occurred")
            
            # Random chance to simulate a restart (1 in 50 iterations)
            if random.random() < 0.02:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🔄 Simulating restart...")
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ♻️ Restarting operations...")
                print("=" * 60)
                
    except KeyboardInterrupt:
        print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 🛑 Script interrupted by user")
    except Exception as e:
        print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] ❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 👋 Additional script stopping...")
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 📈 Total iterations completed: {counter}")
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🕒 Total runtime: {counter * 10} seconds")
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ✅ Script completed successfully!")

if __name__ == "__main__":
    main()
