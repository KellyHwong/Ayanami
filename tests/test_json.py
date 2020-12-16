import json
import requests

json_string = """{"component":{"params":{"schemaVersion":1,"loop":false,"autoPlay":false,"isPlaylistOpen":false,"playlist":[{"audioFileUrl":"https:\/\/img.moegirl.org.cn\/common\/d\/d4\/Cv-30105_link4.mp3","lrcFileUrl":"","title":"Cv-30105 link4.mp3","album":"","artist":"","isExplicit":false,"navigationUrl":"\/File:Cv-30105_link4.mp3","coverImageUrl":"","lrcFileOffset":0}],"compactMode":true,"backgroundColor":"","foregroundColor":"","trackColor":"","thumbColor":""},"name":"sm2-player-fx"}}"""
data = json.loads(json_string)

playlist = data["component"]["params"]["playlist"]
assert len(playlist) == 1
file_url = playlist[0]["audioFileUrl"]
navigation_url = playlist[0]["navigationUrl"]
file_name = navigation_url.split(":")[1]

data = requests.get(file_url).content
with open(file_name, "wb") as f:
    f.write(data)
