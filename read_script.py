import pandas as pd

def read_excel_to_dict(file_path):

    data = pd.read_excel(file_path)
    option_dict = {}

    for _, row in data.iterrows():
        code = row['option_code']
        #value = row['option_values'].strip()
        value = row['option_values']

        if code not in option_dict:
            #option_dict[code] = [value]
            option_dict[code] = value
        else:
            if value not in option_dict[code]:
                #option_dict[code].append(value)
                option_dict[code] = value

    return option_dict

if __name__ == "__main__":
    excel_path = 'options.xlsx'  
    try:
        data_dict = read_excel_to_dict(excel_path)
        #print("Options dhis2 meta_data:")
        for code, values in data_dict.items():
            #print(f"{code}: {values}")
            
            #print( data_dict['back pain'] )
            #print( data_dict['XYZ'] )
            #print( data_dict['ABC'] )  

            #my_dict = {'apple': 1, 'banana': 2, 'cherry': 3}
            key_to_check = 'Lactose Intolerance'

            if data_dict.get(key_to_check) is not None:
                print(f"Key '{key_to_check}' exists.")
            else:
                print(f"Key '{key_to_check}' does not exist.")

    except Exception as e:
        print(f"An error occurred: {e}")
