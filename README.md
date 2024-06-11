# hyperedit-gui

front end for hyperedit

## project summary

this project aims to provide a way to interact with hyperedit that is less cumbersome than the command line

## plan

- Select a video file
- Select "create project" or "load project"
    - create project
        - specify project name
        - specify project parent directory
        - a directory will be created in this parent folder with the following structure
        - ROOT
            - project.json
            - SRTs
                - srt files
            - Clips
                - split clips and previews
            - Audio
                - merged wave files etc
    - load project
        - loads project from directory or project.json file
        - errors if project.json file not valid or directory does not contain a valid project.json file
- Proceed to project settings page
    - Select audio tracks (prepopulated if present in project.json file)

## project.json file

```
{
    "source_video_file": "/Users/jake/Movies/source_video.mkv",
    // not populated until selected
    "tracks": [1, 3]
}
```
