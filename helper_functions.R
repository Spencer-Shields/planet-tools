#Helper functions for pre-processing planetscope data. Vignettes are in comments within the functions.

#Extract metadata from the json files that get downloaded with Planet scenes and organize in a dataframe
ps_meta = function(dir, recursive = T){
  #Returns a tibble of PlanetScope meta data based on metadata.json files in a directory.
  #dir= path to a directory, recursive = whether search for files should encompass all child directories
  
  files = list.files(dir, recursive = recursive, full.names = T)
  jsons = files[str_detect(files, 'metadata\\.json$')]
  if(length(jsons)==0){
    print('No metadata files found in directory.')
  } else {
    jsons_l = lapply(jsons, jsonify::from_json)
    
    json_df <- map_dfr(jsons_l, function(x) {
      tibble(id = x$id, !!!x$properties)
    })
    return(json_df)
  }
}




