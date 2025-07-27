import streamlit as st
import pandas as pd
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="OSRS High Alch Profit Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CATEGORY_ID TO ENGLISH NAME MAPPING (HARDCODED) ---
# This mapping helps categorize items from osrsbox-db's numeric category_id
# to more user-friendly English categories.
CATEGORY_ID_TO_NAME_MAP = {
    1: 'Ammunition', 2: 'Arrows', 3: 'Axes', 4: 'Body', 5: 'Boots', 6: 'Bows',
    7: 'Capes', 8: 'Daggers', 9: 'Gloves', 10: 'Hats', 11: 'Legs', 12: 'Magic Weapons',
    13: 'Necklaces', 14: 'Other', 15: 'Platebodies', 16: 'Polearms', 17: 'Ranged Weapons',
    18: 'Rings', 19: 'Runes', 20: 'Shields', 21: 'Staves', 22: 'Swords', 23: 'Whips',
    24: 'Amulets', 25: 'Crossbows', 26: 'Dart Tips', 27: 'Darts', 28: 'Javelins',
    29: 'Knives', 30: 'Bolts', 31: 'Pickaxes', 32: 'Fishing Rods', 33: 'Harpoons',
    34: 'Nets', 35: 'Bags', 36: 'Containers', 37: 'Consumables', 38: 'Potions',
    39: 'Herbs', 40: 'Seeds', 41: 'Ores and Bars', 42: 'Logs', 43: 'Food',
    44: 'Fish', 45: 'Bones', 46: 'Gems', 47: 'Miscellaneous', 48: 'Tools',
    49: 'Spells', 50: 'Teleportation', 51: 'Crafting materials', 52: 'Farming',
    53: 'Construction', 54: 'Smithing', 55: 'Cooking', 56: 'Firemaking', 57: 'Fletching',
    58: 'Runecrafting', 59: 'Mining', 60: 'Woodcutting', 61: 'Fishing', 62: 'Hunter',
    63: 'Thieving', 64: 'Agility', 65: 'Quests', 66: 'Holiday', 67: 'Tradeable',
    68: 'Untradeable', 69: 'Members', 70: 'Free to play', 71: 'Dyeable',
    72: 'Degradable', 73: 'Chargeable', 74: 'Stackable', 75: 'Noted', 76: 'Quest Items',
    77: 'Achievement Diaries', 78: 'Clues', 78: 'Clues', 79: 'Collection Logs', 80: 'Bounty Hunter',
    81: 'Slayer', 82: 'Construction Materials', 83: 'Jewellery', 84: 'Spirit Shields',
    85: 'God books', 86: 'Ornament kits', 87: 'Imbuable', 88: 'Skilling',
    89: 'Combat', 90: 'Boss drops', 91: 'Minigame rewards', 92: 'Treasure Trails',
    93: 'Grand Exchange', 94: 'Shop supplies', 95: 'Diary rewards', 96: 'Achievement Cape',
    97: 'Music Cape', 98: 'Quest Cape', 99: 'Max Cape', 100: 'Trimmed Max Cape',
    101: 'Veteran Cape', 102: 'Classic Cape', 103: 'Master Combat Cape',
    104: 'Master Skilling Cape', 105: 'Completionist Cape', 106: 'Master Quest Cape',
    107: 'Ultimate Ironman', 108: 'Hardcore Ironman', 109: 'Ironman',
    110: 'Seasonal', 111: 'Deadman Mode', 112: 'League', 113: 'Pest Control',
    114: 'Slayer Helmets', 115: 'Godswords', 116: 'Dragonfire Shields',
    117: 'Barrows equipment', 118: 'Dragon equipment', 119: 'Rune equipment',
    120: 'Adamant equipment', 121: 'Mithril equipment', 122: 'Steel equipment',
    123: 'Iron equipment', 124: 'Bronze equipment', 125: 'Black equipment',
    126: 'White equipment', 127: 'Guthix Vestments', 128: 'Saradomin Vestments',
    129: 'Zamorak Vestments', 130: 'Armadyl armour', 131: 'Bandos armour',
    132: 'Ancient armour', 133: 'Ancestral robes', 134: 'Void Knight armour',
    135: 'Skeletal armour', 136: 'Proselyte armour', 137: 'Obsidian armour',
    138: 'Crystal equipment', 139: 'Tears of Guthix', 140: 'Dagannoth Kings',
    141: 'God Wars Dungeon', 142: 'Zulrah', 143: 'Vorkath', 144: 'Demonic Gorillas',
    145: 'Abyssal Sire', 146: 'Cerberus', 147: 'Kraken', 148: 'Thermonuclear Smoke Devil',
    149: 'Grotesque Guardians', 150: 'Barrows', 151: 'Pest Control', 152: 'Pyramid Plunder',
    153: 'Barbarian Assault', 154: 'Fight Caves', 155: 'Inferno', 156: 'Theatre of Blood',
    157: 'Chambers of Xeric', 158: 'Nightmare', 159: 'Gauntlet', 160: 'Vardorvis',
    161: 'Duke Sucellus', 162: 'The Leviathan', 163: 'The Whisperer',
    164: 'Phantom Muspah', 165: 'ToA', 166: 'Desert Treasure II', 167: 'Forestry'
}

# --- DATA LOADING AND CACHING ---
@st.cache_data(ttl=3600)
def load_item_data():
    """Loads item data from GitHub (osrsbox-db)."""
    try:
        url = "https://raw.githubusercontent.com/osrsbox/osrsbox-db/master/docs/items-complete.json"
        response = requests.get(url)
        response.raise_for_status()
        items_json = response.json()
        
        records = []
        for item_id, item_data in items_json.items():
            item_data_copy = item_data.copy()
            item_data_copy['id'] = int(item_id) 
            records.append(item_data_copy)
        
        df = pd.DataFrame(records)
        
        df.rename(columns={'name': 'Item Name', 'members': 'Is Member'}, inplace=True)

        if 'category_id' not in df.columns:
            df['category_id'] = 0 
        else:
            df['category_id'] = df['category_id'].fillna(0) 
        df['category_id'] = df['category_id'].astype(int) 

        df['examine'] = df['examine'].fillna('') 
        df['highalch'] = df['highalch'].fillna(0).astype(int)

        return df
    except Exception as e:
        st.error(f"Error loading OSRSBox item data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_price_data():
    """Loads real-time prices from the OSRS Wiki API."""
    try:
        headers = {'User-Agent': 'OSRS High Alch Profit Calculator Streamlit App'}
        url = "https://prices.runescape.wiki/api/v1/osrs/latest"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        price_json = response.json()['data']

        df_prices = pd.DataFrame.from_dict(price_json, orient='index')
        df_prices.reset_index(inplace=True)
        df_prices.rename(columns={'index': 'id', 'high': 'Buy Price (GE)', 'low': 'Sell Price (GE)'}, inplace=True)
        df_prices['id'] = pd.to_numeric(df_prices['id'])
        return df_prices[['id', 'Buy Price (GE)', 'Sell Price (GE)']]
    except Exception as e:
        st.error(f"Error loading Grand Exchange prices: {e}")
        return pd.DataFrame()

# --- STYLING AND PROCESSING FUNCTIONS ---
def categorize_item(row):
    """
    Classifies an item into a high-level category using the osrsbox-db category_id
    for robustness, leveraging an internal mapping.
    """
    osrsbox_category_id = row.get('category_id')
    osrsbox_category_name = CATEGORY_ID_TO_NAME_MAP.get(osrsbox_category_id, '').lower()

    # Mapping osrsbox-db categories to more user-friendly high-level categories
    if osrsbox_category_name in ['weapons', 'magic weapons', 'ranged weapons', 'slash weapons', 'stab weapons', 'blunt weapons', 'thrown weapons', 'axes', 'bows', 'daggers', 'polearms', 'staves', 'swords', 'whips', 'crossbows']:
        return 'Weapons'
    if osrsbox_category_name in ['head', 'cape', 'neck', 'amulets', 'body', 'shields', 'legs', 'hands', 'feet', 'rings', 'armour', 'gloves', 'boots', 'platebodies', 'jewellery', 'spirit shields', 'god books', 'ornament kits', '' 'imbued', 'chargeable', 'degradable', 'slayer helmets', 'godswords', 'dragonfire shields', 'barrows equipment', 'dragon equipment', 'rune equipment', 'adamant equipment', 'mithril equipment', 'steel equipment', 'iron equipment', 'bronze equipment', 'black equipment', 'white equipment', 'guthix vestments', 'saradomin vestments', 'zamorak vestments', 'armadyl armour', 'bandos armour', 'ancient armour', 'ancestral robes', 'void knight armour', 'skeletal armour', 'proselyte armour', 'obsidian armour', 'crystal equipment']:
        return 'Armour & Equipment'
    if osrsbox_category_name == 'ores and bars':
        return 'Ores & Bars'
    if osrsbox_category_name == 'logs':
        return 'Logs'
    if osrsbox_category_name == 'potions':
        return 'Potions'
    if osrsbox_category_name == 'runes':
        return 'Runes'
    if osrsbox_category_name in ['bolts', 'arrows', 'darts', 'javelins', 'knives', 'dart tips', 'ammunition']:
        return 'Ammunition'
    if osrsbox_category_name in ['seeds', 'farming']:
        return 'Farming'
    if osrsbox_category_name in ['herblore', 'herbs', 'vials', 'bones', 'gems', 'crafting materials']:
        return 'Crafting Materials'
    if osrsbox_category_name in ['food', 'fish', 'consumables']:
        return 'Food & Consumables'
    if osrsbox_category_name in ['tools', 'pickaxes', 'fishing rods', 'harpoons', 'nets']:
        return 'Tools'
    if osrsbox_category_name in ['construction materials', 'construction', 'smithing', 'cooking', 'firemaking', 'fletching', 'runecrafting', 'skilling']:
        return 'Production Skills'
    if osrsbox_category_name in ['spells', 'teleportation']:
        return 'Magic & Teleport'
    if osrsbox_category_name in ['containers', 'bags']:
        return 'Containers & Bags'
    if osrsbox_category_name in ['quest items', 'clues', 'collection logs', 'achievement diaries', 'diary rewards', 'achievement cape', 'music cape', 'quest cape', 'max cape', 'trimmed max cape', 'veteran cape', 'classic cape', 'master combat cape', 'master skilling cape', 'completionist cape', 'master quest cape']:
        return 'Quest & Achievement Items'
    if osrsbox_category_name in ['boss drops', 'minigame rewards', 'treasure trails', 'bounty hunter', 'slayer', 'combat']:
        return 'Rewards & Drops'
    if osrsbox_category_name in ['grand exchange', 'shop supplies']:
        return 'Trade & Shop' 

    # Fallback if no specific category is found by ID or other primary checks
    name = row['Item Name'].lower() if row['Item Name'] and isinstance(row['Item Name'], str) else ''
    if 'ore' in name or 'bar' in name: return 'Ores & Bars'
    if 'logs' in name or 'plank' in name: return 'Logs'
    if 'potion' in name: return 'Potions'
    if 'rune' in name: return 'Runes'
    if 'food' in name or 'fish' in name: return 'Food & Consumables'

    return 'Other'

def color_profit(val):
    """Returns CSS for text color based on positive/negative value."""
    if val > 0:
        return 'background-color: #2E8B57; color: white;' # Green for positive
    elif val < 0:
        return 'background-color: #DC143C; color: white;' # Red for negative
    else:
        return 'background-color: #A9A9A9; color: black;' # Grey for zero

# --- MAIN INTERFACE CONSTRUCTION ---

st.title("💰 OSRS High Alch Profit Calculator")
st.markdown("📈 Find the most profitable items to buy, cast High Alchemy on, and sell for maximum GP!")
st.markdown("*(The cost of one **Nature Rune** is automatically deducted from the profit.)*")

# Load and merge data
items_df = load_item_data()
prices_df = load_price_data()

if not items_df.empty and not prices_df.empty:
    # --- PROFIT CALCULATION ---
    # Nature Rune ID is 561
    try:
        nature_rune_cost = prices_df.loc[prices_df['id'] == 561, 'Buy Price (GE)'].iloc[0]
    except (IndexError, KeyError):
        st.warning("⚠️ Could not find Nature Rune price (ID 561). Defaulting to 200 GP.")
        nature_rune_cost = 200 # Default value if API fails or rune not found

    df_final = pd.merge(items_df, prices_df, on='id', how='inner')
    
    # Select relevant columns and ensure numeric types
    df_final = df_final[['id', 'Item Name', 'Is Member', 'highalch', 'category_id', 'Buy Price (GE)', 'Sell Price (GE)']].copy()
    
    df_final['highalch'] = df_final['highalch'].fillna(0).astype(int)
    df_final['Buy Price (GE)'] = df_final['Buy Price (GE)'].fillna(0).astype(int)
    df_final['Sell Price (GE)'] = df_final['Sell Price (GE)'].fillna(0).astype(int)

    # Calculate Net Profit
    df_final['Net Profit'] = df_final['highalch'] - df_final['Buy Price (GE)'] - nature_rune_cost
    
    # Ensure Net Profit is integer for formatting
    df_final['Net Profit'] = df_final['Net Profit'].astype(int) 
    
    # Add F2P column (based on 'Is Member')
    df_final['F2P'] = ~df_final['Is Member'] # If not member, then F2P

    # Apply categorization
    df_final['Category'] = df_final.apply(categorize_item, axis=1)
    
    # Drop intermediate/unnecessary columns for final display
    df_final = df_final.drop(columns=['id', 'Is Member', 'category_id'])

    # --- EPIC SIDEBAR FILTERS ---
    st.sidebar.header("⚙️ Filter Options")
    st.sidebar.markdown(f"**Current Nature Rune Cost:** **{nature_rune_cost:,} GP**")
    st.sidebar.markdown("---")

    search_term = st.sidebar.text_input("🔍 Search item by name:", placeholder="Ex: Dragon scimitar")
    
    f2p_filter = st.sidebar.radio(
        "👥 Filter by Membership:",
        ('All Items', 'F2P Only', 'P2P Only'),
        index=0
    )
    
    min_profit = st.sidebar.slider(
        "💰 Minimum Net Profit (GP):",
        min_value=-1000, # Allows viewing items with slight loss if desired
        max_value=20000,
        value=500, # Default to show items with at least 500 GP profit
        step=50
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗂️ Item Categories")
    all_categories = sorted(df_final['Category'].unique())
    selected_categories = []
    
    # Checkbox to select/deselect all
    select_all_categories = st.sidebar.checkbox("✅ Select/Deselect All Categories", value=True)

    if select_all_categories:
        selected_categories = all_categories
    else:
        for category in all_categories:
            if st.sidebar.checkbox(category, value=False, key=f"cat_checkbox_{category}"):
                selected_categories.append(category)
    
    # --- APPLY FILTERS ---
    # Filter for items that can be bought (price > 0) and have an alch value (> 0)
    # and meet minimum profit
    df_filtered = df_final[
        (df_final['Buy Price (GE)'] > 0) & 
        (df_final['highalch'] > 0) & 
        (df_final['Net Profit'] >= min_profit)
    ].copy()

    if search_term:
        df_filtered = df_filtered[df_filtered['Item Name'].str.contains(search_term, case=False, na=False)]
    
    if f2p_filter == 'F2P Only':
        df_filtered = df_filtered[df_filtered['F2P'] == True]
    elif f2p_filter == 'P2P Only':
        df_filtered = df_filtered[df_filtered['F2P'] == False]
    
    if selected_categories:
        df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]
    else:
        # If no categories are selected and "Select All" is not checked, show empty table
        df_filtered = pd.DataFrame(columns=df_filtered.columns)

    # Sort by net profit (descending)
    df_filtered = df_filtered.sort_values(by='Net Profit', ascending=False)

    # --- DISPLAY THE EPIC DATA TABLE ---
    st.header("✨ High Alch Profit Results")
    
    if df_filtered.empty:
        st.info("😔 No items found matching your filter criteria. Try adjusting the filters.")
    else:
        st.markdown(f"Displaying **{len(df_filtered)}** potentially profitable items:")

        display_columns = ['Item Name', 'Buy Price (GE)', 'Sell Price (GE)', 'highalch', 'Net Profit', 'Category', 'F2P']
        
        # Apply conditional styling and format numbers
        styled_df = df_filtered[display_columns].style.applymap(color_profit, subset=['Net Profit'])
        
        styled_df.format({
            'Buy Price (GE)': '{:,.0f} GP', 
            'Sell Price (GE)': '{:,.0f} GP',  
            'highalch': '{:,.0f} GP',        
            'Net Profit': '{:+,d} GP'     
        })

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

else:
    st.error("❌ Failed to load item or price data. Please check your internet connection and refresh the page.")

# --- SUBTLE TWITCH GUYS ---
# Replace 'YOUR_TWITCH_CHANNEL' with your actual Twitch channel name
TWITCH_CHANNEL_NAME = "Gold_Gabe" # <--- REPLACE WITH YOUR TWITCH CHANNEL NAME!
TWITCH_URL = f"https://www.twitch.tv/{'GOLD_GABE'}"

st.sidebar.markdown("---")
st.sidebar.markdown(f"Developed with passion for OSRS. [Join the adventure on Twitch! 📺]({TWITCH_URL})")

st.markdown("---")
st.markdown(f"Brought to you by an OSRS enthusiast. Find me live on [Twitch: {TWITCH_CHANNEL_NAME}](<https://www.twitch.tv/{TWITCH_CHANNEL_NAME}>) 🎮")
