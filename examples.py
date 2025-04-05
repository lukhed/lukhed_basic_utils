from lukhed_basic_utils import matplotlibBarCharts, matplotlibBasics, matplotlibScatter
from lukhed_basic_utils import githubCommon as gC
from lukhed_basic_utils import osCommon as osC
from lukhed_basic_utils import timeCommon as tC

def simple_scatter_chart_with_best_fit():
    chart_data = matplotlibBasics.create_sub_plots()

    matplotlibScatter.add_scatter_points_to_chart(chart_data["ax"], 
                                                  [1, 2, 3, 4, 5, 6, 7, 8], 
                                                  [2, 4, 10, 8, 10, 12, 19, 16], 
                                                  best_fit_line=True)
    chart_data["fig"].show()

def bar_chart_with_images():
    # First create the cache dir if it doesn't already exist
    osC.check_create_dir_structure(['lukhedCache'])
    teams = ["TB", "CAR", "MIN", "GB", "DET"]
    data = [10, 20, 30, 40, 50]
    colors = ["red", "blue", "purple", "green", "silver"]

    # Use lukhed NFL logos
    base_url = "https://raw.githubusercontent.com/lukhed/lukhed_sports_league_data/main/images/nfl/logos"
    logo_urls = [
        f"{base_url}/15.png",
        f"{base_url}/0.png",
        f"{base_url}/20.png",
        f"{base_url}/11.png",
        f"{base_url}/10.png"
    ]

    # download the images to the cache dir if they don't already exist
    logo_paths = []
    for url in logo_urls:
        temp_fp = osC.create_file_path_string(["lukhedCache", osC.extract_file_name_given_full_path(url)])
        if osC.check_if_file_exists(temp_fp):
            logo_paths.append(temp_fp)
            
        else:
            print("Downloading image from URL:", url)
            gC.get_github_image(None, None, None, provide_full_url=url, save_path=temp_fp)
            tC.sleep(1)
            logo_paths.append(temp_fp)

    # create the shart and show it
    fig = matplotlibBarCharts.bar_chart_with_images_as_labels(
        teams, 
        data, 
        logo_paths, 
        y_range_tuple=(0, 70), 
        bar_colors=colors, 
        bar_width_multiplier=1.2, 
        image_y_offset=8,
        show_image=True)