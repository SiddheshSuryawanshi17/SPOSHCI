# Operators (basic user actions)
def move_mouse(to):
    print(f"Move mouse to {to}")

def click(button="left"):
    print(f"Click {button} button")

def wait(seconds):
    print(f"Wait for {seconds} seconds")

# Method: Add single item to cart
def add_item_to_cart(item_name):
    print(f"\nGoal: Add '{item_name}' to cart")
    move_mouse(f"item '{item_name}' image")
    click()
    wait(1)  # simulate loading item details page
    move_mouse("'Add to Cart' button")
    click()
    wait(1)  # simulate item added to cart confirmation
    print(f"'{item_name}' added to cart successfully.")

# Selection rule: For multiple items, repeat method for each
def add_multiple_items_to_cart(items):
    print(f"\nGoal: Add multiple items to cart: {items}")
    for item in items:
        add_item_to_cart(item)
    print("\nAll items added to cart.")

# Simulate user interaction
items_to_add = ["Laptop", "Wireless Mouse", "USB-C Cable"]
add_multiple_items_to_cart(items_to_add)



