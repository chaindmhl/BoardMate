import cv2
import numpy as np

# Function to calculate IOU (Intersection over Union) between two bounding boxes
def calculate_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # Calculate coordinates of intersection rectangle
    x_left = max(x1, x2)
    y_top = max(y1, y2)
    x_right = min(x1 + w1, x2 + w2)
    y_bottom = min(y1 + h1, y2 + h2)

    # Calculate area of intersection rectangle
    intersection_area = max(0, x_right - x_left) * max(0, y_bottom - y_top)

    # Calculate area of both bounding boxes
    box1_area = w1 * h1
    box2_area = w2 * h2

    # Calculate IOU
    iou = intersection_area / float(box1_area + box2_area - intersection_area)
    return iou

# Function to calculate distance between two points
def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to perform object detection
def detect_objects(image, net, classes, confidence_threshold=0.5, iou_threshold=0.4):
    height, width = image.shape[:2]  # Modified to handle grayscale images

    # Create a blob from the image
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)

    # Set the input to the network
    net.setInput(blob)

    # Forward pass
    outputs = net.forward(net.getUnconnectedOutLayersNames())

    # Lists to store detected objects
    boxes = []
    confidences = []
    class_ids = []

    # Iterate through each output layer
    for output in outputs:
        # Iterate through each detection
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Filter out weak detections
            if confidence > confidence_threshold:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Calculate bounding box coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # Check for overlapping boxes
                skip_box = False
                for i in range(len(boxes)):
                    box = boxes[i]
                    iou = calculate_iou((x, y, w, h), box)
                    if iou > iou_threshold:
                        if confidence > confidences[i]:
                            # Replace the old box with the new one if it has higher confidence
                            boxes[i] = (x, y, w, h)
                            confidences[i] = confidence
                            class_ids[i] = class_id
                        skip_box = True
                        break

                if not skip_box:
                    boxes.append((x, y, w, h))
                    confidences.append(confidence)
                    class_ids.append(class_id)

    return boxes, confidences, class_ids

# Function to sort detected objects based on their bounding box positions and distance from a specified point
def sort_objects_by_distance(boxes, class_ids, classes, point):
    object_dict = {}
    for i, (box, class_id) in enumerate(zip(boxes, class_ids)):
        class_name = classes[class_id]
        midpoint_x = box[0] + box[2] / 2  # Calculate midpoint x-coordinate
        midpoint_y = box[1] + box[3] / 2  # Calculate midpoint y-coordinate
        distance = calculate_distance(point, (midpoint_x, midpoint_y))  # Calculate distance to specified point
        object_dict[i + 1] = (class_name, box, distance)

    # Sort by distance
    sorted_object_dict = dict(sorted(object_dict.items(), key=lambda x: x[1][2]))
    return sorted_object_dict

# Function to group bounding boxes based on x-coordinate ranges and assign sequence numbers
def group_and_sequence(sorted_boxes, sorted_keys):
    grouped_boxes = {}
    for seq_num, (_, (x, _, w, _), _) in zip(sorted_keys, sorted_boxes):
        if 50 <= x < 150:
            group_num = 1
        elif 250 <= x < 350:
            group_num = 2
        elif 450 <= x < 600:
            group_num = 3
        elif 750 <= x < 850:
            group_num = 4
        elif 950 <= x < 1100:
            group_num = 5
        else:
            continue
        
        if group_num not in grouped_boxes:
            grouped_boxes[group_num] = []
        
        grouped_boxes[group_num].append(seq_num)

    # Assign sequence numbers to each group
    sequence_num = 1
    final_grouped_boxes = {}
    for group_num, seq_nums in grouped_boxes.items():
        for seq_num in sorted(seq_nums):
            final_grouped_boxes[sequence_num] = seq_num
            sequence_num += 1
    
    return final_grouped_boxes
