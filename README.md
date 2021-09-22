# lunar_crush_rest
An unofficial wrapper for the Lunar Crush social metrics api!

USAGE:
 - initiate the connection by calling lc = CrushClient(api_key='YOUR_API_KEY')
 - call lc.help() to access the Lunar Crush API docs which will tell you about valid request inputs
 - all data calls are made through lc.get_info() which has one required argument, req_type, which by default, is 'assets'
 - all other arguments you may wish to make can be passed in as keyword arguments, which are automatically encoded.
    - for example, if you wanted to get information on tyler winkelvoss's (@tyler) tweets over the past 300 days, you would enter:
        tyler_info = lc.get_info(req_type='influencer', screen_name='tyler', days=300)
 - the standard return of the call is a dictionary with the keys 'config', 'usage', and 'data'. use ['data'].attr_names to get a list of the attributes of the data object
 - Will be making usage edits!
 - Please make use of the demo Jupyter Notebook!

 - Warning: Exceptions not yet handled well! Still working on this!
