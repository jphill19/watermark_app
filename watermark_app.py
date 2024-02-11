import shlex
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk

# Note to anyone reading this, the more work I did to this, the better idea classes would've been. I regret not doing so and I apologize for the long code. I will be using classes in the future

horizonal_grid_number=12
vertical_grid_number=24
### Global Variables
image= None

# Checks if a image is selected
selected_image=None
# This is used in my highlight function, in order to prevent the program to consinously change of default menu This variable stores the previous state of the selected_image variable
selected_image_previous_state=None

# Image IDS contain the ids of all the images on the canvas
image_ids = []

# List to store the Photoimage objects to prevent them from being garbage collected
images = {}

# Keep the same copy of the image dictionary, but in the PIL Image format
images_pil = {} # This is needed because the PhotoImage object is not compatible with the resize function. The resize function only works with the PIL Image object

# This list contains the file paths of the images
image_list = []


# The zoom level of the image. The default
zoom = 100


zoom_label = None  # Define zoom_label at the top of your code

# This is the original image with the alpha channel. This is being utilized to keep track of the original image with an alpha channel. Reason? The original image with an alpha channel is being modified when the opacity is changed. This is to keep track of the original image with the original alpha channel in order to revert any changes.
# In short, I am keeping a copy of the original image with the original alpha channel. I can increase the opacity of an image with an alpha channel but I can't decrease the opacity, so my work around is to have this dictionary to pull the original image if I need to decrase the opacity
original_image_alpha= {}

##################################  RESIZE FUNCTION ###########################################


# def resize_canvas(event):
#     if image_list is None:
#         return
#     ##print("resizing")

#     draw_grid()

#     for i in image_ids:
#         # Get the center coordinates of the canvas
#         center_x = canvas.winfo_width() // 2
#         center_y = canvas.winfo_height() // 2

#         # Get the current coordinates of the image (note that coords gets the coordinates of the top left corner of the image)
#         current_x, current_y = canvas.coords(i)

#         # Calculate the center of the image (Becuase the coords function gets the coordinates of the top left corner of the image)
#         if zoom == 100:
#             image_center_x = current_x + images[i]['image_width'] // 2
#             image_center_y = current_y + images[i]['image_width'] // 2
#         else:
#             image_center_x = current_x + images[i]['zoom_width'] // 2
#             image_center_y = current_y + images[i]['zoom_height'] // 2
    
#         # Calculate the distance to move the image to the new center of the canvas
#         dx = center_x - image_center_x
#         dy = center_y - image_center_y

#         # Move the image to the new center of the canvas
#         canvas.move(i, dx, dy)

#         #print(canvas.winfo_width(), canvas.winfo_height())



##################################  RESIZE FUNCTION END ###########################################

################################## CENTER IMAGE FUNCTION ###########################################
def center_image(image_id, image):
    # Get the center coordinates of the canvas
    center_x = canvas.winfo_width() // 2
    center_y = canvas.winfo_height() // 2

    # Get the current coordinates of the image (note that coords gets the coordinates of the top left corner of the image)
    current_x, current_y = canvas.coords(image_id)

    # Calculate the center of the image (Becuase the coords function gets the coordinates of the top left corner of the image)
    image_center_x = current_x + image.width() // 2
    image_center_y = current_y + image.height() // 2

    # Calculate the distance to move the image to the new center of the canvas
    dx = center_x - image_center_x
    dy = center_y - image_center_y

    # Move the image to the new center of the canvas
    canvas.move(image_id, dx, dy)

    #To rehighlight the image
    highlight_image()


##################################  DRAG FUNCTIONS START ###########################################

def on_press(event):
    global selected_image
    item_id = canvas.find_withtag("current")
 
    # Store the initial mouse coordinates
    if len(item_id) > 0 and item_id[0] in image_ids:
        image_id = item_id[0]
        selected_image=image_id
        #print(canvas.find_withtag("current"))
        #print("pressed")
        highlight_image()
        canvas.tag_bind(image_id, '<Motion>', on_drag)
        canvas.tag_bind(image_id, '<ButtonRelease-1>', on_release)
        start_x = event.x
        start_y = event.y
        # Store the initial mouse coordinates ( start.x  & start_y) and the image_id to pass to the drag function and on release function
        canvas.data = {'start_x': start_x, 'start_y': start_y, 'image_id': image_id}
    else:
        selected_image=None
        highlight_image()
        #print("No image was clicked")


def on_drag(event):
    # Get the image ID from the canvas data, and store it in a local variable.
    highlight_image()
    image_id = canvas.data['image_id']

    # Calculate the distance moved by the mouse. Event.x and event.y are the current mouse coordinates and canvas.data['start_x'] and canvas.data['start_y'] are the initial mouse coordinates
    delta_x = event.x - canvas.data['start_x']
    delta_y = event.y - canvas.data['start_y']

    # Move the image by the calculated distance. # The move function takes the image id, and the distance to move the image in the x and y directions
    canvas.move(image_id, delta_x, delta_y)

    # Update the starting coordinates for the next drag event
    canvas.data['start_x'] = event.x
    canvas.data['start_y'] = event.y

    # Get the new coordinates of the image. The bbox function returns the coordinates of the bounding box of the image. The bounding box is the smallest rectangle that can contain the image
    x1, y1, x2, y2 = canvas.bbox(image_id)
        # x1, y1 are the coordinates of the top left corner of the image and x2, y2 are the coordinates of the bottom right corner of the image

    # Get the current width and height of the canvas
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    # Calculate the center of the image
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # Calculate the size of the grid (width and height of each grid cell)
    grid_size_vertical= width//vertical_grid_number # The // operator is the floor division operator. It returns the quotient of the division rounded down to the nearest integer
    grid_size_horizontal=height//horizonal_grid_number 

    # Reminder, the canvas is a grid of cells. The size of each cell is grid_size_vertical by grid_size_horizontal which are Global Variables

    tolerance = 3  # Define your tolerance here

    # only doing center because the assumption if the center is touching the grid line, then the whole image is touching the grid line
    center = ((x1 + x2) / 2, (y1 + y2) / 2)
    center_left = (x1, (y1 + y2) / 2)
    center_right = (x2, (y1 + y2) / 2)
    center_top = ((x1 + x2) / 2, y1)
    center_bottom = ((x1 + x2) / 2, y2)

    points = [center, center_left, center_right, center_top, center_bottom]

    canvas.delete('green_grid_line')

    points = [center, center_left, center_right, center_top, center_bottom]

    for point in points:
        # point is a tuple containing the x and y coordinates of the point

        # Calculate the nearest grid lines for this point
            # center_x is the x coordinate of the center of the image. We divide it by grid_size_vertical, which results in a number that represents how many vertical grid cells the center of the image is away from the origin (0,0)
            # We round this number to the nearest integer, and then multiply it by grid_size_vertical to get the x coordinate of the nearest vertical grid line
        nearest_x = round(point[0] / grid_size_vertical) * grid_size_vertical
        nearest_y = round(point[1] / grid_size_horizontal) * grid_size_horizontal

        # Calculate the distance to the nearest grid lines
        dx = nearest_x - point[0]
        dy = nearest_y - point[1]

        # Adjust the position towards the nearest grid lines
        if abs(dx) <= tolerance:
            #print(f"dx for point {point} is less than tolerance")
            canvas.move(image_id, dx * 0.1, 0)
        if abs(dy) <= tolerance:
            #print(f"dy for point {point} is less than tolerance")
            canvas.move(image_id, 0, dy * 0.1)
            # Here's how it works utilizing dy as an example:
            #     dy is the distance from the center of the image to the nearest horizontal grid line.
            #     If dy is less than or equal to the tolerance, the image is close enough to the grid line that it should start to snap to it.
            #     The image is moved towards the grid line by a fraction of the distance dy. This fraction is 0.1, or 10%.
            #     By moving the image only a fraction of the distance, the image moves slower as it gets closer to the grid line, creating a smooth snapping effect.
            

    # Draw the horizontal lines
    for i in range(0, height, grid_size_horizontal):
        # any returns True if any of the values in the list are True
        # Abs returns the absolute value of a number example abs(-5) = 5, abs(5) = 5
        # p[1] is the y coordinate of the point
        # i is the y coordinate of the grid line
        # abs(p[1] - i) is the distance between the point and the grid line
        # if the distance between the point and the grid line is less than or equal to the tolerance, then the point is close enough to the grid line that it change the color value to green
        color = "#9CAE8B" if any(abs(p[1] - i) <= tolerance for p in points) else None
        # 
        canvas.create_line([(0, i), (width, i)], fill=color, tags='green_grid_line', width=3) if color=="#9CAE8B" else None

        
    # Draw the vertical lines
    for i in range(0, width, grid_size_vertical):
        # same as above but for the x coordinates
        color = "#9CAE8B" if any(abs(p[0] - i) <= tolerance for p in points) else None
        canvas.create_line([(i, 0), (i, height)], fill=color, tags='green_grid_line', width=3) if color =="#9CAE8B" else None

    canvas.tag_lower('green_grid_line')
    canvas.tag_lower('grid_line')
    

def on_release(event):
    canvas.delete('green_grid_line')
    # Get the image ID from the canvas data
    image_id = canvas.data['image_id']
    
    # Unbind the drag and release events
    canvas.tag_unbind(image_id, '<Motion>')
    canvas.tag_unbind(image_id, '<ButtonRelease-1>')

def highlight_image():
    global selected_image_previous_state

    # Check if an image is selected
    if selected_image:
    

        # Delete any existing rectangles
        canvas.delete('highlight')

        # Get the coordinates of the image
        bbox = canvas.bbox(selected_image)

        # Create a rectangle around the image
        rectangle_id = canvas.create_rectangle(bbox, outline='red', width=3, tags='highlight')

        if selected_image_previous_state != selected_image:
            # Enable the change size button. The after is to allow ample amount of times to allow the buttons to load
            window.after(100, default_menu, 'enabled')
            selected_image_previous_state = selected_image

        # Store the rectangle ID so you can delete it later if needed
    else:
        canvas.delete('highlight')
        #print("No image is selected")

        # If the state has changed, update the menu
        if selected_image_previous_state is not None:
            # Disable the change size button
            default_menu('disabled')
            selected_image_previous_state = None

def unhightlight_image():
    global selected_image_previous_state
    # Check if an image is selected
    if selected_image is None:
        # Disable the change size button
        default_menu('disabled')

        selected_image_previous_state = None

        canvas.delete('highlight')
        #print("Unhighlighted")
##################################  DRAG FUNCTIONS END ###########################################

##################################  DROP FUNCTION START ##########################################

def on_drop(event):
    if zoom != 100:
        reset_zoom()
    # Parse the data from the event to get the file paths
    file_paths = shlex.split(event.data.replace("{", "'").replace("}", "'"))
    #print(file_paths)

    # Add the first file path to the image list
    image_list.append(file_paths[0])
    #print(f"This is the image list: {image_list}")

    # Initialize the total height and widthof the images
   
    pil_image = Image.open(file_paths[0])
    #for image_file in image_list:
    # Load the image
    image = tk.PhotoImage(file=file_paths[0])

    

    # Calculate the position to place the image
    # Images are placed vertically one below the other

    # center_x = canvas.winfo_width() // 2
    # center_y = canvas.winfo_height() // 2

    # Draw the image on the canvas. 0,0 are placeholders for the x and y coordinates. The center_image function will move the image to the center of the canvas
    image_id = canvas.create_image(0,0, image=image, anchor='nw')

    
    image_width = image.width()
    image_height = image.height()

    image_data = {'image_id': image_id, 'image': image, 'pil_image': pil_image, 'original_image_copy':image, 'image_width': image_width, 'image_height': image_height, 'zoom_level': 100, 'zoom_width': image.width(), 'zoom_height': image.height(), 'opacity':[False, 100,], 'alpha': False}

    # Add the image to the images dictiory to prevent it from being garbage collected & the images_pil dictionary to allow resizing
    images[image_id]=image_data



    images_pil[image_id]=pil_image

    center_image(image_id, image)
    image_ids.append(image_id)
    # Bind the mouse events to the new image_id
    canvas.tag_bind(image_id, '<ButtonPress-1>', on_press)

    # Update the total height of the images
    #total_height += image.height()

# Adjust the size of the canvas to match the total size of the images
    canvas.config(width=1920, height=1000)
##################################  DROP FUNCTION END ############################################
from tkinter import filedialog


def upload_image():
    # Open a file dialog and get the path of the selected file
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
    
    if zoom != 100:
        reset_zoom()

    if file_path:
        # Open the image file, as image object and a pil_image object
        photo = Image.open(file_path)
        pil_image = Image.open(file_path)
        
        # Convert the image object to a PhotoImage object
        image = ImageTk.PhotoImage(photo)
        
        # Create an image item on the canvas
        image_id = canvas.create_image(0, 0, anchor="nw", image=image)
        center_image(image_id, image)

        # Store the image data in a dictionary
        image_width = image.width()
        image_height = image.height()
        image_data = {'image_id': image_id, 'image': image, 'pil_image': pil_image, 'original_image_copy':image, 'image_width': image_width, 'image_height': image_height, 'zoom_level': 100, 'zoom_width': image.width(), 'zoom_height': image.height(), 'opacity':[False, 100 ], 'alpha':False}

        
        # Keep a reference to the image object to prevent it from being garbage collected
        images[image_id]=image_data
        images_pil[image_id]=pil_image

        image_ids.append(image_id)
        image_list.append(file_path)
        canvas.tag_bind(image_id, '<ButtonPress-1>', on_press)
##################################  DRAW GRID FUNCTION ###########################################
def draw_grid():
    # Clear the canvas
    canvas.delete('grid_line')

    # Get the current width and height of the canvas
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    grid_size_vertical= width//vertical_grid_number
    grid_size_horizontal=height//horizonal_grid_number



    # Draw the vertical lines
    for i in range(0, width, grid_size_vertical):
        canvas.create_line([(i, 0), (i, height)], fill='grey', tags='grid_line', dash=(4, 4))

    # Draw the horizontal lines
    for i in range(0, height, grid_size_horizontal):
        canvas.create_line([(0, i), (width, i)], fill='grey', tags='grid_line', dash=(4, 4))
    
    # Move the grid lines to the back of the stacking order
    canvas.tag_lower('grid_line')
##################################  DRAW GRID FUNCTION END ###########################################

##################################  DEFAULT MENU FUNCTION START ######################################
 
# Global dictionary to store images



# Create a frame to hold the default menu buttons
def default_menu(mode):
    global zoom_label

    # Delete all the frames, to get back to  main menu
    delete_all_frames()

    default_menu_frame = tk.Frame(window)
    default_menu_frame.grid(row=0, column=0, sticky='w')
    #default_menu_frame.config(bg="#2E2E2E")

    ###Create Buttons
    #Upload Button
    upload_button = ttk.Button(default_menu_frame, text="Upload Image", command=upload_image, style="TButton")
    upload_button.pack(side=tk.LEFT)

    #Save Button
    save_button = ttk.Button(default_menu_frame, text="Save Image", command=save_image_function, style="TButton")
    save_button.pack(side=tk.LEFT)

    # Filler label
    filler_label = ttk.Label(default_menu_frame, text=" ", style="TLabel")
    filler_label.pack(side=tk.LEFT, padx=15)

    #Change Size Button
    change_size_button = ttk.Button(default_menu_frame, text="Change Size", command=change_size, style="TButton")
    change_size_button.pack(side=tk.LEFT, padx=10)
    # have to disable the change size button unless the image is selected
    if mode == "disabled":
        change_size_button.config(state=tk.DISABLED)
    elif mode == "enabled":
        change_size_button.config(state=tk.NORMAL)

    # Filler label
    filler_label = ttk.Label(default_menu_frame, text=" ", style="TLabel")
    filler_label.pack(side=tk.LEFT, padx=15)

    #Change Opacity Button
    change_opacity_button = ttk.Button(default_menu_frame, text="Change Opacity", command=change_opacity, style="TButton")
    change_opacity_button.pack(side=tk.LEFT, padx=10),
    if mode == "disabled":
        change_opacity_button.config(state=tk.DISABLED)
    elif mode == "enabled":
        change_opacity_button.config(state=tk.NORMAL)

    # Filler label
    filler_label = ttk.Label(default_menu_frame, text=" ", style="TLabel")
    filler_label.pack(side=tk.LEFT, padx=15)

    # Move Label
    move_label = ttk.Label(default_menu_frame, text="Move Image: ", style="TLabel")
    move_label.pack(side=tk.LEFT)
    move_label.config(state=tk.DISABLED)

    # Move image to front
    # forward_image= Image.open('./Icons/up_arrow.png')
    # forward_image = forward_image.resize((18, 18))
    # forward_photo= ImageTk.PhotoImage(forward_image)
    # forward_photo.image = forward_photo

    move_image_to_front_button = ttk.Button(default_menu_frame,image=button_images['forward'], command=move_image_to_front)
    move_image_to_front_button.pack(side=tk.LEFT)
    if mode == "disabled":
        move_image_to_front_button.config(state=tk.DISABLED)
        create_tooltip(move_image_to_front_button, "Move Image to Front")
    elif mode == "enabled":
        move_image_to_front_button.config(state=tk.NORMAL)
        create_tooltip(move_image_to_front_button, "Move Image to Front")

    # Move image to back
    # backward_image= Image.open('./Icons/down_arrow.png')
    # backward_image = backward_image.resize((18, 18))
    # backward_photo= ImageTk.PhotoImage(backward_image)
    # backward_photo.image = backward_photo
        
    move_image_to_back_button = ttk.Button(default_menu_frame, image=button_images['backward'], command=move_image_to_back)
    move_image_to_back_button.pack(side=tk.LEFT)
    if mode == "disabled":
        move_image_to_back_button.config(state=tk.DISABLED)
    elif mode == "enabled":
        move_image_to_back_button.config(state=tk.NORMAL)
        create_tooltip(move_image_to_back_button, "Move Image to Back")

    # Filler label
    filler_label = ttk.Label(default_menu_frame, text=" ", style="TLabel")
    filler_label.pack(side=tk.LEFT, padx=15)


    # Zoom label
    zoom_label = ttk.Label(default_menu_frame, text=f"Zoom: {zoom}%", style="TLabel")
    zoom_label.pack(side=tk.LEFT,)
    #zoom_label.grid(row=0, column=2, sticky='e')


    # Zoom In Button
    # zoom_in_image = Image.open('./Icons/zoom_in.png')
    # zoom_in_image = zoom_in_image.resize((18, 18))  # Resize the image
    # zoom_in_photo = ImageTk.PhotoImage(zoom_in_image)
    # zoom_in_photo.image = zoom_in_photo
    zoom_in_button = ttk.Button(default_menu_frame, image=button_images['zoom_in'], command=zoom_in, style="TButton", width=15)
    zoom_in_button.pack(side=tk.LEFT)
    create_tooltip(zoom_in_button, "Zoom In")

    # Zoom Out Button
    # zoom_out_image = Image.open('./Icons/zoom_out.png')
    # zoom_out_image = zoom_out_image.resize((18, 18))  # Resize the image
    # zoom_out_photo = ImageTk.PhotoImage(zoom_out_image)
    # zoom_out_photo.image = zoom_out_photo
    zoom_out_button = ttk.Button(default_menu_frame, image=button_images['zoom_out'], command=zoom_out, style="TButton", width=15)
    zoom_out_button.pack(side=tk.LEFT)
    create_tooltip(zoom_out_button, "Zoom Out")

    if mode =="update":
        zoom_label.config(text=f"Zoom: {zoom}%")




##################################  DEFAULT MENU FUNCTION END ########################################

##################################### MOVING FUNCTION START ##########################################

def move_image_to_front():
    if selected_image:
        canvas.tag_raise(selected_image)
        # to raise the the hightlighted rectangle to the front
        highlight_image()

def move_image_to_back():
    if selected_image:
        canvas.tag_lower(selected_image)
        canvas.tag_lower('grid_line')

##################################### MOVING FUNCTION END ############################################
        
##################################  CHANGE SIZE FUNCTION START #######################################
def change_image_size(new_width, new_height):
    global selected_image, original_image_alpha
    # Get the original PIL Image
    if images[selected_image]['alpha'] == True:
        original_image = original_image_alpha[selected_image]
    else:
        original_image = images_pil[selected_image]

    print(original_image.mode)
    # Resize the image
    #print(new_height, new_width)
    resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Store the new pil image inside original_image_alpha if the image has an alpha channel
    if images[selected_image]['alpha'] == True:
        original_image_alpha[selected_image] = resized_image
    
    # Convert the resized image to a PhotoImage object
    resized_photo = ImageTk.PhotoImage(resized_image)

    # Update the image on the canvas
    canvas.itemconfigure(selected_image, image=resized_photo)

    # Update the PhotoImage in the images list
    images[selected_image]['image'] = resized_photo
    images[selected_image]['pil_image'] = resized_image
    images[selected_image]['image_width'] = new_width
    images[selected_image]['image_height'] = new_height


    # Update the resized PIL Image in the pil_images dictionary
    images_pil[selected_image] = resized_image

    # Center the image
    center_image(selected_image, resized_photo)
    highlight_image()
    print(images[selected_image]['opacity'][0])
    if images[selected_image]['opacity'][0] == True:
        check_alpha_channel()
        change_opacity_level(images[selected_image]['opacity'][1], mode=2)

def exit_size_changes(mode = 2, **kwargs):
    ''' Function to exit the change size menu. Mode 1 is to exit the menu and go back to the default menu. Mode 2 is to exit the menu and save the changes. The kwargs are the new_width and new_height of the image'''
    
   
    if mode == 1:
        back_to_default_menu()
    elif mode == 2:
        new_width = kwargs.get('new_width')
        new_height = kwargs.get('new_height')
        #print(f"Here are the new width and height: {new_width}, {new_height}")
        change_image_size(new_width= new_width, new_height=new_height)
        back_to_default_menu()








def create_tooltip(widget, text):
    def enter(event):
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)  # Remove window decorations
        tooltip.wm_geometry("+%d+%d" % (event.x_root, event.y_root))  # Position the tooltip
        label = tk.Label(tooltip, text=text, bg='white', relief='solid', borderwidth=1)
        label.pack()
        widget.tooltip = tooltip  # Keep a reference to the tooltip

    def leave(event):
        widget.tooltip.destroy()  # Destroy the tooltip

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)



def change_size():
    
    if zoom != 100:
        reset_zoom()
    center_image(selected_image, images[selected_image]['image']) # Center the image

    if selected_image:
        # Get the image object from the images list
        change_image = images[selected_image]['image']
        #print(f"Here is the image: {change_image}, and the width is {change_image.width()}")
        original_width, original_height = change_image.width(), change_image.height()

        #print(f"The following are: {original_width}, {original_height}")
        
        # Delete all the frames (This is to prevent the frames from stacking on top of each other), note that all my button options are frames
        delete_all_frames()
        change_size_menu_frame= tk.Frame(window)
        change_size_menu_frame.grid(row=0, column=0, sticky='w')
        
        # Height
        height_label = ttk.Label(change_size_menu_frame, text="Height: ")
        height_label.pack(side=tk.LEFT)
        height_entry = ttk.Entry(change_size_menu_frame, width=10)
        height_entry.insert(0, original_height)
        height_entry.pack(side=tk.LEFT)

        # Width
        width_label = ttk.Label(change_size_menu_frame, text="Width: ")
        width_label.pack(side=tk.LEFT)
        width_entry = ttk.Entry(change_size_menu_frame, width=10)
        width_entry.insert(0, original_width)
        width_entry.pack(side=tk.LEFT)

        # Refresh images
        # refresh_image = Image.open('./Icons/refresh_icon.png')
        # refresh_image = refresh_image.resize((25, 20))
        # refresh_photo = ImageTk.PhotoImage(refresh_image)
        refresh_button = ttk.Button(change_size_menu_frame, image=button_images['refresh'], command=lambda: change_image_size(new_width=int(width_entry.get()), new_height=int(height_entry.get())))
        create_tooltip(refresh_button, "Refresh Image")
        # refresh_button.image = refresh_photo
        refresh_button.pack(side=tk.LEFT, padx=3)


        # Save Changes
        # save_image = Image.open('./Icons/submit_icon.png')
        # save_image = save_image.resize((30, 20))  # Resize the image
        # save_photo = ImageTk.PhotoImage(save_image)
        save_changes_button = ttk.Button(change_size_menu_frame, image=button_images['save'], command=lambda: exit_size_changes(new_width=int(width_entry.get()), new_height=int(height_entry.get())))
        create_tooltip(save_changes_button, "Save Changes")
        #save_changes_button.image = save_photo
        save_changes_button.pack(side=tk.LEFT, padx=3)

        # Cancel Changes
        # cancel_image = Image.open('./Icons/cancel_icon.png')
        # cancel_image = cancel_image.resize((21,20))  # Resize the image
        # cancel_photo = ImageTk.PhotoImage(cancel_image)
        cancel_changes_button = ttk.Button(change_size_menu_frame, image=button_images['cancel'], command=lambda: exit_size_changes(mode=1))
        create_tooltip(cancel_changes_button, "Cancel Changes")
        #cancel_changes_button.image = cancel_photo
        cancel_changes_button.pack(side=tk.LEFT, padx=3)

##################################  CHANGE SIZE FUNCTION END #########################################

################################## CHANGE OPACITY FUNCTION START ####################################
"""
Summary: Resolving RGBA Image Resizing After Opacity Modification

Issue:
- Encountered difficulties resizing RGBA images (images with an alpha channel) after their opacity had been modified.
- The root cause was identified as the application using outdated image data stored in the 'original_image_alpha' dictionary, which did not reflect the latest opacity adjustments.

Solution:
- Implemented an update mechanism for the 'original_image_alpha' dictionary to ensure it always contains the most recent version of the image data after any modifications, including opacity changes.
- This update mechanism involves refreshing the corresponding entry in 'original_image_alpha' whenever an image's opacity is adjusted, ensuring subsequent operations like resizing work with the updated image data.

Key Changes:
1. After modifying an image's opacity, the updated image data is now also stored back in the 'original_image_alpha' dictionary, overwriting the previous entry.
2. This ensures that any future operations that rely on 'original_image_alpha' for image data (such as resizing) are using the most current version of the image.

Benefits:
- Ensures consistency and integrity of image data throughout the application, particularly for RGBA images that undergo multiple modifications.
- Prevents issues related to using outdated image data, enabling seamless resizing and other operations post-opacity modification.

Note: This solution emphasizes the importance of managing image data references carefully, especially when dealing with mutable image objects and multiple image transformations.

"""


    

# alpha=False

none_alpha_images = {}
scale_value_label = None  # Define scale_value_label at the top of your code



def exit_opacity_changes(value):
    change_opacity_level(value)
    back_to_default_menu()


def check_alpha_channel():
    global original_image_alpha, none_alpha_images
    if selected_image:
        pil_image = images[selected_image]['pil_image']
        if (selected_image) in  none_alpha_images:
            print("The image is already in the dictionary")
            images[selected_image]['alpha'] = False
            return
        
        if pil_image.mode in ('RGBA', 'LA') or (pil_image.mode == 'P' and 'transparency' in pil_image.info):
            print("The image has an alpha channel.")
            images[selected_image]['alpha'] = True
            if (selected_image) in original_image_alpha:
                print("The image is already in the dictionary")
            else: 
                print("The image is not in the dictionary")
                print(selected_image)
                original_image_alpha[selected_image] = pil_image
        else:
            images[selected_image]['alpha']  = False
            none_alpha_images[selected_image] = pil_image

def change_opacity_level(value, mode=1):
    if images[selected_image]['alpha']  == False:
        round_value=round(float(value))
        #scale_value_label.config(text=f"Current scale value: {round_value}")
        # mode 1 indicates that it came from the change_opacity function. Mode 2 indicates that it came from the change_size function
        # The change_size function will not have the scale_value_label, so it will not be updated. It calls this function to refresh the image with the saved opacity level that we store in our images dictionary
        if mode == 1:
            change_opacity(mode=2, round_value=round_value)
        
        pil_image = images[selected_image]['pil_image']
        pil_image = pil_image.convert("RGBA")
        data = list(pil_image.getdata())
        for i, item in enumerate(data):
            data[i] = item[0], item[1], item[2], int(round_value) * 255 // 100
        pil_image.putdata(data)
        change_image = ImageTk.PhotoImage(pil_image)
        canvas.itemconfig(selected_image, image=change_image)
        images[selected_image]['image'] = change_image
        images[selected_image]['pil_image'] = pil_image
        images[selected_image]['opacity'] = [True, round_value]
        highlight_image()

    if images[selected_image]['alpha']  == True:
        import numpy as np
        round_value = round(float(value))
        # scale_value_label.config(text=f"Current scale value: {round_value}")
        if mode == 1:
            change_opacity(mode=2, round_value=round_value)
        original_image_data = np.array(original_image_alpha[selected_image])  
        print(original_image_data)

        print(original_image_data.ndim)
        if original_image_data.ndim == 2:  
            # Replicate the grayscale data across the RGB channels
            # Convert grayscale to RGB by replicating the grayscale data across the RGB channels
            rgb_image_data = np.repeat(original_image_data[:, :, np.newaxis], 3, axis=2)

            # If the colors appear inverted, invert them back
            rgb_image_data = 255 - rgb_image_data  # Invert colors

            # Create an alpha channel with full opacity for each pixel
            alpha_channel = 255 * np.ones((original_image_data.shape[0], original_image_data.shape[1]), dtype=np.uint8)

            # Combine the RGB data and alpha channel to get an RGBA image
            rgba_image_data = np.dstack((rgb_image_data, alpha_channel))

            # Convert the NumPy array to a PIL image
            original_pil_image = Image.fromarray(rgba_image_data, 'RGBA')

            # Correct the rotation if the image is rotated
            # Adjust the angle based on the actual rotation of your images
            #original_pil_image = original_pil_image.rotate(90, expand=True)  # Rotate 90 degrees counterclockwise

            # data = np.array(original_pil_image)  # Convert original image to numpy array

            # # Scale value from 0-100 to 0-255
            # opacity_scale = (int(round_value) / 100) * 255

            # # Modify the alpha channel based on the slider's value
            # red, green, blue, alpha_channel = data.T
            # new_alpha = ((alpha_channel / 255) * opacity_scale).astype(np.uint8)
            # new_data = np.dstack([red, green, blue, new_alpha])

            # # Create a new image from the modified data
            # new_pil_image = Image.fromarray(new_data, 'RGBA')

            # # Convert the PIL Image back to a PhotoImage for Tkinter
            # change_image = ImageTk.PhotoImage(new_pil_image)

            # # Update the image on the canvas
            # canvas.itemconfig(selected_image, image=change_image)

            # # Update the image in the images list
            # images[selected_image]['image'] = change_image
            # images[selected_image]['pil_image'] = new_pil_image

            # # Ensure the image object is kept alive by keeping a reference
            # images[selected_image]['photo_image'] = change_image  # Store this to prevent garbage collection
            # images[selected_image]['opacity'] = [True, round_value]
            # # Highlight the image
            # highlight_image()


        elif original_image_data.ndim == 3:
            original_pil_image = Image.fromarray(original_image_data, 'RGBA')
            
        data = np.array(original_pil_image)  # Convert original image to numpy array

        # Scale value from 0-100 to 0-255
        opacity_scale = (int(round_value) / 100) * 255

        # Modify the alpha channel based on the slider's value
        # red, green, blue, alpha_channel = data.T
        red, green, blue, alpha_channel = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
        new_alpha = ((alpha_channel / 255) * opacity_scale).astype(np.uint8)
        new_data = np.dstack([red, green, blue, new_alpha])

        # Create a new image from the modified data
        new_pil_image = Image.fromarray(new_data, 'RGBA')

        # Convert the PIL Image back to a PhotoImage for Tkinter
        change_image = ImageTk.PhotoImage(new_pil_image)

        # Update the image on the canvas
        canvas.itemconfig(selected_image, image=change_image)

        # Update the image in the images list
        images[selected_image]['image'] = change_image
        images[selected_image]['pil_image'] = new_pil_image

        # Ensure the image object is kept alive by keeping a reference
        images[selected_image]['photo_image'] = change_image  # Store this to prevent garbage collection
        images[selected_image]['opacity'] = [True, round_value]
        # Highlight the image
        highlight_image()


def change_opacity(mode=1, round_value=None):
    global scale_value_label
    if mode == 1:
        if selected_image:
            # # Get the image object from the images list
            
            check_alpha_channel()
            
            if images[selected_image]['opacity'][0] == False:
                opacity_level = 100
                average_opacity_scaled = 100
            else:
                opacity_level = images[selected_image]['opacity'][1]
                average_opacity_scaled = images[selected_image]['opacity'][1]

            # Delete all the frames (This is to prevent the frames from stacking on top of each other), note that all my button options are frames
            delete_all_frames()

            change_opacity_menu_frame= tk.Frame(window)
            change_opacity_menu_frame.grid(row=0, column=0, sticky='w')

            # Create a label to display the value of the scale
            scale_value_label = tk.Label(change_opacity_menu_frame, text=f"Current scale value: {round(average_opacity_scaled)}", font=("Arial", 10))
            scale_value_label.pack(side=tk.LEFT, padx=3)

            scale = ttk.Scale(change_opacity_menu_frame, from_=1, to=100, command=change_opacity_level, orient=tk.HORIZONTAL, length=200)
            scale.pack(side=tk.LEFT, padx=3)
            scale.set(round(opacity_level))

            # Save Changes
            # save_image = Image.open('./Icons/submit_icon.png')
            # save_image = save_image.resize((30, 20))  # Resize the image
            # save_photo = ImageTk.PhotoImage(save_image)
            save_changes_button = ttk.Button(change_opacity_menu_frame, image=button_images['save'], command=lambda: back_to_default_menu())
            create_tooltip(save_changes_button, "Save Changes")
            #save_changes_button.image = save_photo
            save_changes_button.pack(side=tk.LEFT, padx=3)

            # Cancel Changes
            #cancel_opacity = Image.open('./Icons/cancel_icon.png')
            #cancel_opacity = cancel_opacity.resize((21,20))  # Resize the image
            #cancel_opacity_photo = ImageTk.PhotoImage(cancel_opacity)
            cancel_opacity_button = ttk.Button(change_opacity_menu_frame, image=button_images['cancel'], command= lambda: exit_opacity_changes(opacity_level))
            create_tooltip(cancel_opacity_button, "Cancel Changes")
            #cancel_opacity_button.image = cancel_opacity_photo
            cancel_opacity_button.pack(side=tk.LEFT, padx=3)
    if mode == 2:
        scale_value_label.config(text=f"Current scale value: {round_value}")

        


################################## CHANGE OPACITY FUNCTION END ######################################



################################## ZOOM FUNCTION START ###########################################

def zoom_in():
    global zoom
    zoom += 10
    #print(f"Zoom level: {zoom}")
    for i in image_ids:
        # Get the original image
        original_image = images[i]['pil_image']

        # Calculate the new zoom level
        images[i]['zoom_level'] += 10

        # Calculate the new dimensions
        images[i]['zoom_width'] = original_image.width * images[i]['zoom_level'] // 100
        images[i]['zoom_height'] = original_image.height * images[i]['zoom_level'] // 100

        # Create a copy of the original image and resize it
        resized_image = original_image.resize((images[i]['zoom_width'], images[i]['zoom_height']))

        # Convert the resized image to a PhotoImage (Tkinter uses PhotoImage objects to display images)
        images[i]['image'] = ImageTk.PhotoImage(resized_image)

        # Update the image on the canvas
        canvas.itemconfig(i, image=images[i]['image'])

    # Update the zoom label
    default_menu("update")
    if selected_image:
        highlight_image()

def zoom_out():
    global zoom
    zoom -= 10
    #print(f"Zoom level: {zoom}")
    for i in image_ids:
        # Get the original image
        original_image = images[i]['pil_image']

        # Calculate the new zoom level
        images[i]['zoom_level'] -= 10

        # Calculate the new dimensions
        images[i]['zoom_width'] = original_image.width * images[i]['zoom_level'] // 100
        images[i]['zoom_height'] = original_image.height * images[i]['zoom_level'] // 100

        # Create a copy of the original image and resize it
        resized_image = original_image.resize((images[i]['zoom_width'], images[i]['zoom_height']))

        # Convert the resized image to a PhotoImage (Tkinter uses PhotoImage objects to display images)
        images[i]['image'] = ImageTk.PhotoImage(resized_image)

        # Update the image on the canvas
        canvas.itemconfig(i, image=images[i]['image'])

    # Update the zoom label
    default_menu("update")

    if selected_image:
        highlight_image()

def reset_zoom():
    global zoom
    zoom = 100
    #print(f"Zoom level: {zoom}")
    for i in image_ids:
        # Get the original image
        original_image = images[i]['pil_image']

        # Calculate the new zoom level
        images[i]['zoom_level'] = 100

        # Calculate the new dimensions
        images[i]['zoom_width'] = original_image.width * images[i]['zoom_level'] // 100
        images[i]['zoom_height'] = original_image.height * images[i]['zoom_level'] // 100

        # Create a copy of the original image and resize it
        resized_image = original_image.resize((images[i]['zoom_width'], images[i]['zoom_height']))

        # Convert the resized image to a PhotoImage (Tkinter uses PhotoImage objects to display images)
        images[i]['image'] = ImageTk.PhotoImage(resized_image)

        # Update the image on the canvas
        canvas.itemconfig(i, image=images[i]['image'])

    # Update the zoom label
    default_menu("update")

    if selected_image:
        highlight_image()

############################### FIND ALL FRAMES FUNCTION START #######################################
def delete_all_frames():
    #print("Finding all frames")
    for widget in window.winfo_children():
        if isinstance(widget, tk.Frame):
            #print(f"Here is the {widget}")
            widget.destroy()

################################## FIND ALL FRAMES FUNCTION END #####################################
            
################################## SAVE IMAGE FUNCTION START ########################################
# def save_image_function():
#     # Get the file path to save the image
#     file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
#     #print(file_path)
#     if file_path:
#         # Get the image from the canvas
#         image = canvas.postscript(colormode='color')

#         # Save the image to the file path
#         with open(file_path, "w") as file:
#             file.write(image)
            
def save_image_function():
    # get rid of the highlighted rectangle
    #if no images on screen, return
    if images == {}:
        return
    global selected_image
    selected_image = None
    unhightlight_image()

    # Modify the canvas to exclude the grid lines and set background to white
    canvas.itemconfig('grid_line', state='hidden')
    canvas.config(bg="white")

    # Force Tkinter to update the GUI immediately
    window.update_idletasks() 

    from PIL import ImageGrab
    min_x = 1920
    min_y = 1920

    max_x = 0
    max_y = 0

    for image in image_ids:
        # Get the image ID
        image_id = image

        # Get the image coordinates
        x1, y1, x2, y2 = canvas.bbox(image_id)
        # The coordinates are returned in the format (x1, y1, x2, y2), where (x1, y1) is the top-left corner of the bounding box and (x2, y2) is the bottom-right corner.
        
        # Convert the image coordinates to screen coordinates
        x1 += canvas.winfo_rootx()
        y1 += canvas.winfo_rooty()
        x2 += canvas.winfo_rootx()
        y2 += canvas.winfo_rooty()

        # Update the minimum and maximum x and y values
        min_x = min(min_x, x1)
        min_y = min(min_y, y1)
        max_x = max(max_x, x2)
        max_y = max(max_y, y2)

    



    # # Grab the screen area corresponding to the canvas
    image = ImageGrab.grab(bbox=(min_x, min_y, max_x, max_y))



    # # Save the image

    # Get the file path to save the image
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])

    # Save the image
    if file_path:
        image.save(file_path)
    
    # Unhide the grid lines and set the background back to the original color
    canvas.itemconfig('grid_line', state='normal')
    canvas.config(bg="#e5fff6")

###############################  TKINTER CONFIGURATIONS START ########################################
window = TkinterDnD.Tk()
window.title("Watermark Application")
window.iconbitmap('./Icons/Design.ico')
window.minsize(width=1050, height=1000)
window.config(padx=0)
#window.configure(bg="#2E2E2E")


### Button for my widgets
button_images = {}

def load_images():
    # Load the images and store them in the dictionary
    forward_image = Image.open('./Icons/up_arrow.png')
    forward_image = forward_image.resize((18, 18))
    button_images['forward'] = ImageTk.PhotoImage(forward_image)

    backward_image = Image.open('./Icons/down_arrow.png')
    backward_image = backward_image.resize((18, 18))
    button_images['backward'] = ImageTk.PhotoImage(backward_image)

    zoom_in_image = Image.open('./Icons/zoom_in.png')
    zoom_in_image = zoom_in_image.resize((18, 18))
    button_images['zoom_in'] = ImageTk.PhotoImage(zoom_in_image)

    zoom_out_image = Image.open('./Icons/zoom_out.png')
    zoom_out_image = zoom_out_image.resize((18, 18))
    button_images['zoom_out'] = ImageTk.PhotoImage(zoom_out_image)

    refresh_image = Image.open('./Icons/refresh_icon.png')
    refresh_image = refresh_image.resize((25, 20))
    button_images['refresh'] = ImageTk.PhotoImage(refresh_image)

    save_image = Image.open('./Icons/submit_icon.png')
    save_image = save_image.resize((30, 20))
    button_images['save'] = ImageTk.PhotoImage(save_image)

    cancel_image = Image.open('./Icons/cancel_icon.png')
    cancel_image = cancel_image.resize((21,20))
    button_images['cancel'] = ImageTk.PhotoImage(cancel_image)
# load the images for the buttons
load_images()



###Create a canvas
canvas = tk.Canvas(window, width=1920, height=950, highlightbackground="black", highlightthickness=2, bg="#e5fff6")
canvas.grid(row=1, column=0, columnspan=10, sticky="nsew")
canvas.drag_data = None

canvas.after(100, draw_grid)

#### Styling
button_colors = {"foreground": "#2E2E2E", "background": "#2E2E2E", "activeforeground": "#F0F0F0", "activebackground": "#2E2E2E"}

style = ttk.Style()
style.configure("TButton", font=("Arial", 10, "bold"), width=20, relief=tk.RAISED, foreground="#2E2E2E") 

style.configure("TLabel", font=("Arial", 12))
style.configure("TLabelBold", font=("Arial", 15, "bold"))
style.configure("TLabelNormal", font=("Arial", 15))

default_menu('disabled')

### Configure the rows and columns to expand
window.grid_columnconfigure(0, weight=0)
#window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=0)
window.grid_rowconfigure(1, weight=0)

#############################  TKINTER CONFIGURATIONS END ##########################################

############################## BACK TO DEFAULT MENU START ############################################


def back_to_default_menu():
    # Unbind the drag and release events for the selected image and unhighlight the image
    global selected_image, scale_value_label
    # This is a global variable that contains the label configuration for the change_opacity function, to which I want to reset, incase the user is coming from change opacity screen
    scale_value_label = None
    selected_image = None
    unhightlight_image()
    # Delete all the frames, to get back to the main menu
    delete_all_frames()
    default_menu("disabled")

############################## BACK TO DEFAULT MENU END ############################################


########################################## BINDINGS START ##########################################

###Enable dropping onto the canvas
canvas.drop_target_register(DND_FILES)
canvas.dnd_bind('<<Drop>>', on_drop)

# Bind the on_press function to the canvas
canvas.bind('<Button-1>', on_press)

### Bind the function to the window's <Configure> event
#window.bind('<Configure>', resize_canvas)

#window.bind('<Control-v>', paste_image)
########################################## BINDINGS END ##########################################
  
# Call the function to load the images


window.mainloop()
