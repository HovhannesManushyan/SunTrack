import numpy as np
from datetime import datetime
from suncalc import get_position
from pytz import timezone, utc
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

def handle_scroll(event):
    """Handle mouse scroll events for zooming"""
    ax = event.inaxes
    if ax is None:
        return
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    scale_factor = 1.3
    
    if event.button == 'up':
        scale = 1/scale_factor
    else:
        scale = scale_factor
    
    center_x = event.xdata
    center_y = event.ydata
    
    new_xlim = [
        center_x - (center_x - xlim[0]) * scale,
        center_x + (xlim[1] - center_x) * scale
    ]
    new_ylim = [
        center_y - (center_y - ylim[0]) * scale,
        center_y + (ylim[1] - center_y) * scale
    ]
    
    ax.set_xlim(new_xlim)
    ax.set_ylim(new_ylim)
    plt.draw()

def find_locations_from_shadow(object_height, shadow_length, date_time):
    """
    Find possible locations on Earth based on object height and shadow length.
    
    Args:
        object_height (float): Height of the object in same units as shadow
        shadow_length (float): Length of shadow in same units as object
        date_time (datetime): UTC datetime of the measurement
    """
    lat_resolution = 0.5  
    lon_resolution = 0.5  
    
    lats = np.arange(-60, 85, lat_resolution)
    lons = np.arange(-180, 180, lon_resolution)
    

    lons_grid, lats_grid = np.meshgrid(lons, lats)
    

    if date_time.tzinfo is None:
        date_time = utc.localize(date_time)
    

    sun_altitudes = np.zeros_like(lons_grid)

    for i in range(len(lats)):
        for j in range(len(lons)):
            pos = get_position(date_time, lons[j], lats[i])
            sun_altitudes[i, j] = pos['altitude']  # in radians

    
    calculated_shadows = object_height / np.tan(sun_altitudes)
    
    differences = np.abs((calculated_shadows - shadow_length) / shadow_length)
    
    differences[calculated_shadows < 0] = np.nan
    differences[sun_altitudes <= 0] = np.nan
    
    fig = plt.figure(figsize=(15, 10))
    
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax.add_feature(cfeature.OCEAN, alpha=0.3)
    ax.add_feature(cfeature.LAND, alpha=0.3)
    ax.add_feature(cfeature.LAKES, alpha=0.3)
    ax.add_feature(cfeature.RIVERS, linewidth=0.5)
    

    threshold = 0.1
    masked_differences = np.ma.masked_where(
        (differences > threshold) | np.isnan(differences), 
        differences
    )

    im = plt.pcolormesh(lons_grid, lats_grid, masked_differences, 
                   transform=ccrs.PlateCarree(),
                   cmap='viridis', alpha=0.7)
    
    cbar = plt.colorbar(im, orientation='horizontal', pad=0.05, aspect=50)
    cbar.set_label('Relative difference (smaller is better)')
    
    title = (f"Possible locations at {date_time.strftime('%Y-%m-%d %H:%M UTC')}\n"
             f"Object height: {object_height}, Shadow length: {shadow_length}")
    plt.title(title)
    
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    
    fig.canvas.mpl_connect('scroll_event', handle_scroll)
    
    flat_diffs = differences.flatten()
    flat_lats = lats_grid.flatten()
    flat_lons = lons_grid.flatten()

    valid_indices = ~np.isnan(flat_diffs)
    valid_diffs = flat_diffs[valid_indices]
    valid_lats = flat_lats[valid_indices]
    valid_lons = flat_lons[valid_indices]
    
    best_indices = np.argsort(valid_diffs)[:5]
    
    print("\nMost likely locations (lat, lon, difference):")
    for idx in best_indices:
        print(f"Lat: {valid_lats[idx]:.2f}°, Lon: {valid_lons[idx]:.2f}°, Difference: {valid_diffs[idx]:.2%}")
    
    plt.show()


if __name__ == "__main__":

    from datetime import datetime
    import pytz

    now = datetime.now()
    specific_time = datetime.now()

    
    find_locations_from_shadow(
        object_height=98,
        shadow_length=185,
        date_time=specific_time
    )