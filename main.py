import streamlit as st
import requests
import datetime
import time

st.set_page_config(
    page_title="Torn revive chance calculator",
    page_icon="🏥",
    )

# initializing the state of the submit button to false
if 'submit_button_clicked' not in st.session_state:
    st.session_state.submit_button_clicked = False

#function to change the submit button state so that we know that is has been pressed
def submit_button_clicked():
    st.session_state.submit_button_clicked = True

def calculate_revive_chance(api, reviver_skill):
    revive_score = 0
    now = datetime.datetime.now().timestamp()
    
    # since revives later than 24 hrs have no effect, so we only need to check revives which happened since then
    reive_check_cutoff_time = int(now) - 86400
    api_response = requests.get(f"https://api.torn.com/user/?selections=revives&from={reive_check_cutoff_time}&key={api}&comment=rev_chance_calc").json()

    #loop through the API respose and check each timestamp of the revives
    for key in api_response["revives"]:
        
        #we need to find the number of seconds since each revive happened to calculate their individual weight in revive score
        time_since_current_revive = now - api_response["revives"][key]["timestamp"]
        
        # add the current revive score to the total revive score
        revive_score  += 1 - (time_since_current_revive/86400)

    revive_chance = 90 + (reviver_skill/10) - revive_score*(8- (reviver_skill/25))
    return revive_chance


st.title("Torn revive chance calculator")
column1, column2 = st.columns(2)

reviver_skill = column1.number_input("Reviver skill:",min_value=0, max_value=100, value=100)
user_api_key = column2.text_input("Your API key:")

st.button("✅Submit", on_click=submit_button_clicked)

if st.session_state.submit_button_clicked:
    
    # error handling incase the user didn't input API key
    if not user_api_key:
        st.markdown(''' :red[Please input your minimal access API key]''' )
        time.sleep(2)
        st.session_state.submit_button_clicked = False
        st.rerun()

    final_revive_chance = int(calculate_revive_chance(user_api_key, reviver_skill))
    if final_revive_chance >=75:
        text_colour = "green"
    elif final_revive_chance <=25:
        text_colour = "red"
    else:
        text_colour = "orange"

    st.markdown(f"Revive Success Chance: {f''':{text_colour}[{final_revive_chance}%]'''}")