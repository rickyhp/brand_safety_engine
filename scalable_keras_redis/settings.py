############ MongoDB settings ################

MONGODB_NAME = 'adtech'
MONGODB_TABLE = 'measure'

Website_Folder_Column = 'website_folder'
Website_Column = 'website'
Image_Name_Column = 'image_name'
Result_Column = 'result'
Suspicious_Column = 'suspicious'

Category_Alcohol = 'Alcohol'
Category_Gambling = 'Gambling'
Category_Nudity = 'Nudity'

Text_url = 'http://ec2-34-213-187-5.us-west-2.compute.amazonaws.com:5001'

############# Threshold #########################

advice_threshold_unsafe = 0.9
stoping_threshold = 0.9
suspicious_threshold = 0.7

############# Result JSON object keys should synchronize with UI variables ######################

Advice = 'advice'
Font_Color = 'font_color'
Probabilities = 'probabilities'
Text = 'text'

Unknown_Value = 'Unknown'
Safe_Value = 'Safe'
Unsafe_Value = 'Unsafe'

Unknown_Color = 'yellow'
Safe_Color = 'green'
Unsafe_Color = 'red'

slice_width = 500
slice_height = 500
slice_step = 250

############# Models will be used in the program ##########################

Categories_In_Program = [Category_Alcohol, Category_Gambling, Category_Nudity]

def default_result():
    result = {}
    for category in Categories_In_Program:
        result[category] = -1
    return result
