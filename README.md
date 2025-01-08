# SunTrack
A simple script to identify potential locations of the object based on time, object size and shadow size in arbitrary units(ratio is what matters)

The inner workings are very simple for each point in the map the script calculated the location of the sun at the given time.
And based on the altitude of the sun calculates the shadow size of the object aka object_size / tan(θ).
Given this the script maps all locations in the map where estimated shadow size is closer to the given shadow size.

```
             Sun •
    Altitude  /|
    Angle -> /θ|
            /  | Object
           /   | Height (h)
          /    |
         /     |
    ----+------+----
    Horizon  Shadow 
          Length (s)
```

# Example output
![image](https://github.com/user-attachments/assets/24997691-52e5-44b4-a973-e909dc7a252a)


# Credits
The ideas are based from the wonderful code snippets provided by https://github.com/bellingcat/ShadowFinder 
