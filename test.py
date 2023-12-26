def video_duration_to_seconds(duration_string):
    components = duration_string.split(':')

    if len(components) == 3: hours, minutes, seconds = map(int, components)
    elif len(components) == 2: hours, minutes, seconds = 0, int(components[0]), int(components[1])
    elif len(components) == 1: hours, minutes, seconds = 0, 0, int(components[0])
    else: hours, minutes, seconds = 0, 0, 0  # Invalid format

    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

# Examples:
duration_string_1 = "1:00:01"
duration_string_2 = "2:56"
duration_string_3 = "0:03"

total_seconds_1 = video_duration_to_seconds(duration_string_1)
total_seconds_2 = video_duration_to_seconds(duration_string_2)
total_seconds_3 = video_duration_to_seconds(duration_string_3)

print("Total duration in seconds (Example 1):", total_seconds_1)
print("Total duration in seconds (Example 2):", total_seconds_2)
print("Total duration in seconds (Example 3):", total_seconds_3)