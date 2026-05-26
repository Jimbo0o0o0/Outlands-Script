import re
from collections import Counter

# Define the input and output file paths
input_file = r"C:\Program Files (x86)\Ultima Online Outlands\ClassicUO\Data\Client\JournalLogs\2025_05_31_16_52_53_journal.txt"
output_file = r"C:\Users\dcorr\Documents\received_items_grouped.txt"

# Function to extract and regroup data from lines containing "System: You receive:"
def extract_and_group_received_items(input_file, output_file):
    try:
        # Open the input file for reading
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # List to store extracted items
        received_items = []
        
        # Regular expression to match the pattern, ignoring the timestamp
        pattern = r'System: You receive: (.+)'
        
        # Iterate through each line and extract matches
        for line in lines:
            match = re.search(pattern, line.strip())
            if match:
                # Extract item and remove trailing period and extra whitespace
                item = match.group(1).strip().rstrip('.')
                received_items.append(item)
        
        # Use Counter to group and count similar items
        item_counts = Counter(received_items)
        
        # Sort items alphabetically for better readability
        sorted_items = sorted(item_counts.items(), key=lambda x: x[0])
        
        # Write the grouped data to the output file
        with open(output_file, 'w', encoding='utf-8') as file:
           
            file.write("=====================================\n")
            file.write(f"Total Unique Items: {len(sorted_items)}\n")
            file.write(f"Total Items Received: {sum(item_counts.values())}\n\n")
            #file.write("Item Received | Count\n")
            #file.write("--------------|------\n")
            for item, count in sorted_items:
                file.write(f"{item:13s} Amount: {count}\n")
        
        # Print the results to the console
       
        print("=====================================")
        print(f"Total Unique Items: {len(sorted_items)}")
        print(f"Total Items Received: {sum(item_counts.values())}")
        #print("\nItem Received | Count")
        #print("--------------|------")
        for item, count in sorted_items:
            print(f"{item:13s} Amount: {count}")
        
        print(f"\nResults have been written to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
if __name__ == "__main__":
    extract_and_group_received_items(input_file, output_file)