import json
from typing import List
from hyperedit.srt import parse_srt

_SRTS_SINGLETON = None

_KEY_EDITED_START_TIME = "edited_start_time"
_KEY_EDITED_END_TIME = "edited_end_time"
_KEY_ENABLED = "enabled"

class Srt:
    def __init__(self, entry) -> None:
        self.id = entry[0]
        self.original_start_time = entry[1]
        self.original_end_time = entry[2]
        self.text = entry[3]
        # TODO: load these from srt.json
        self.edited_start_time = None
        self.edited_end_time = None
        self.enabled = True

    def to_primitive(self):
        return (self.id, self.original_start_time, self.original_end_time, self.text)
    
    def to_edit_json(self):
        json = {}
        json[_KEY_EDITED_START_TIME] = self.edited_start_time
        json[_KEY_EDITED_END_TIME] = self.edited_end_time
        json[_KEY_ENABLED] = self.enabled
        return json

def _LoadSrtEdits(srt_file_path) -> dict:
    srt_edit_path = srt_file_path + ".json"
    edits = {}
    try:
        # read edits
        with open(srt_edit_path, 'r') as srt_edit_file:
            json_edits = json.load(srt_edit_file)
            for key in json_edits.keys():
                edits[key] = (json_edits[key].get(_KEY_EDITED_START_TIME, None), json_edits[key].get(_KEY_EDITED_END_TIME, None), json_edits[key].get(_KEY_ENABLED, True))
    except FileNotFoundError:
        # write an empty edits file
        with open(srt_edit_path, 'w') as srt_edit_file:
            srt_edit_file.write("{}")
    except json.decoder.JSONDecodeError:
        print(f"Error decoding json in {srt_edit_path}")
    return edits

def LoadSrts(srt_file_path) -> List[Srt]:

    global _SRTS_SINGLETON

    # parse SRTs from SRT file
    primitive_srts = parse_srt(srt_file_path)
    srts = []
    for srt in primitive_srts:
        srts.append(Srt(srt))

    # parse edits from edits file
    edits = _LoadSrtEdits(srt_file_path)

    # for any present edits, enhance the "Srt"
    for srt in srts:
        edit = edits.get(srt.id, (None, None, True))
        srt.edited_start_time = edit[0]
        srt.edited_end_time = edit[1]
        srt.enabled = edit[2]

    _SRTS_SINGLETON = srts

def SaveEdits(srt_file_path):
    # overwrites?
    edits = {}
    with open(srt_file_path + ".json", 'w') as srt_edit_file:
        for srt in GetSrts():
            edits[srt.id] = srt.to_edit_json()
        srt_edit_file.write(json.dumps(edits))

def GetSrts() -> List[Srt]:
    global _SRTS_SINGLETON
    if _SRTS_SINGLETON is None:
        print("SRTs have not been loaded yet.")
        return []
    return _SRTS_SINGLETON