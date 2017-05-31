```shell
pip install -r requirements.txt
brew install jq mongodb
```
```python
python get_all_house.py [110000] --output-dir bj$(date '+%Y%m%d')
./import_db.sh bj$(date '+%Y%m%d')
```
If you want to restart your scrapy you may need `rm bj$(date '+%Y%m%d')/checkpoint`.

If you need add some filter conditions you can refer `load_bj.sh`
