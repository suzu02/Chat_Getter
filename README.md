# Chat Getter
趣味で作成したGUIアプリケーションです。

YouTubeのアーカイブ動画からチャットデータを取得して、CSVファイルとして出力します。

![python](https://img.shields.io/badge/python-v3.10-blue)
![pyperclip](https://img.shields.io/badge/pyperclip-v1.8.2-blue)
![pysimplegui](https://img.shields.io/badge/pysimplegui-v4.60.4-blue)
![pytchat](https://img.shields.io/badge/pytchat-v0.5.5-blue)
![license](https://img.shields.io/badge/license-MIT-green)



## 概要
* ライブ配信後のアーカイブ動画を対象としています。
* 上記以外のライブ配信中の動画や投稿動画は対象外です。
* チャットデータは「すべてのチャット」から取得され、ライブ開始前の待機中のチャットも含まれます。
* 利用にあたっては、ネットワーク接続が必要です。
* 出力される項目は以下のとおりです。

| 項目名 | 概要 | 補足 | 出力例 |
| :--- | :--- | :---- | :---- |
| num | 連番 | - | - |
| d_time | チャット送信時の年月日と時間 | - | 2023-01-01 12:00:01 |
| e_time | チャット送信時の経過時間 | 待機中のチャットはマイナス表記 | -10:00, 5:00, 10:00 ... |
| name | チャット送信者のYouTubeアカウント名 | - | - |
| message | チャットの内容 | 絵文字等は「:(ショートカット テキスト):」 | テキスト:poultry_leg:テキスト |
| type | チャットの種類 | newSponsorはチャンネル登録 | superChat, textMessage, superSticker, newSponsor |
| unit | スーパーチャット等の通貨単位 | 円は記号、その他は通貨コード(ISO 4217) | ￥, USD, SGD, TWD ... |
| amount | スーパーチャット等の金額 | 数値のみ | 1,234.0 |
| channel | チャット送信者のYouTubeチャンネルURL | - | http://www.youtube.com/channel/(チャンネル名) |



## 必要な環境
アプリケーションを利用するために以下の環境が必要です。(動作確認はWindows環境のみ)
* [Python](https://www.python.org/) 3.10 
* [pyperclip](https://github.com/asweigart/pyperclip) 1.8.2  BSD License
* [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI) 4.60.4  GNU Lesser General Public License v3 or later (LGPLv3+)
* [pytchat](https://github.com/taizan-hokuto/pytchat) 0.5.5  MIT License

このリポジトリをクローンして、`pip install -r requirements.txt`コマンドを実行することで、任意の環境に必要なライブラリをまとめてインストールすることができます。

また、以下の手順により実行ファイル化(exe化)して使用することも可能です。



## exe化の手順([auto-py-to-exe](https://github.com/brentvollebregt/auto-py-to-exe))
1. クローンしたこのリポジトリまで移動
2. 次のコマンドを実行 `auto-py-to-exe chat_getter.py`
3. auto-py-to-exeのGUIが表示されるので、
* Onefileは`One Directory`を選択
* Console Windowは`Window Based (hide the console)`を選択
* Iconは「browse」ボタンからクローンされた`icon.ico`ファイルを設定
* Additional Filesは「Add Files」ボタンからクローンされた`icon.ico`ファイル、`chat_getter.py`ファイルを設定
* 「CONVERT .PY TO .EXE」ボタンをクリックして処理開始
4. 「output」ディレクトリが作成されるので、その中の「chat_getter」ディレクトリに`chat_getter.exe`があることを確認

上記の手順は新たな仮想環境を作成して、必要なライブラリをインストールしてから実行することを推奨します。

必要最低限のライブラリだけで構成されるので、exeファイルのサイズが小さくなり、起動時間も短縮されます。



## 使用方法
アプリを起動すると以下のような画面が表示されます。

<image width='500' alt='初期のメイン画面' src=https://user-images.githubusercontent.com/117723810/216195747-fa40cce1-1216-4ea7-8d2e-4e09d5f56038.png>

### 1. 動画のURLまたはIDを設定
処理したい動画のURLまたはIDを設定してください。

IDとは、URLの中に含まれるランダムな11文字程度の英数字や記号の組み合わせのことです。


### 2. 保存PATHの設定
出力されるCSVファイルの保存場所を設定してください。

「選択」ボタンをクリックすると「名前を付けて保存」画面が表示されます。
  
<image width='600' alt='初期のメイン画面' src=https://user-images.githubusercontent.com/117723810/216196422-a91e454b-3fcb-4b70-a2b1-b46cfa5514f3.png>

画面内で保存したいフォルダを選択、ファイル名を入力して「保存」ボタンをクリックすると自動で保存PATHが設定されます。

ファイル名の末尾は、拡張子「.csv」を付けなくても大丈夫です。その場合は自動で付与されます。


### 3. 開始ボタンをクリック
設定されたURLまたはIDに問題がなければ、処理画面に遷移して処理が開始されます。(遷移後の処理画面は最小化されます。)

<image width='500' alt='開始時のメイン画面' src=https://user-images.githubusercontent.com/117723810/216196474-f0e82450-ca14-47a5-8363-cb6033f02157.png>
<image width='250' alt='処理画面' src=https://user-images.githubusercontent.com/117723810/216196478-636ee0bc-e73b-4a2c-8b1a-5997959912d6.png>

処理に必要な手順は以上です。

URLまたはIDに問題がある場合は、処理は開始せずエラーメッセージが表示されます。
  
<image width='500' alt='エラー時のメイン画面' src=https://user-images.githubusercontent.com/117723810/216196590-3bf0b50b-a8a3-4518-8284-e928bfe7d4a5.png>

エラーの場合、主に以下の理由が考えられます。
* 対象外の動画のURLまたはIDが設定されている場合
* ライブ配信終了後、まだチャットデータが反映されていないアーカイブ動画を設定した場合
* チャットのリプレイ機能が許可されていないアーカイブ動画を設定した場合
* チャット機能がOFFにされているライブ配信のアーカイブ動画を設定した場合

上記以外にも、チャットデータが存在しない、もしくは、チャットデータが取得できない状態にある動画はエラーとなります。


### 処理の中止
処理を中止したい場合は、処理画面の「中止」ボタンをクリックしてください。

確認画面が表示されるので、さらに「OK」をクリックすると処理は中止され、最初の画面に戻ります。


### 処理終了
すべての処理が終了すると終了画面が表示されるので、「戻る」ボタンをクリックすると最初の画面に戻ります。
  
<image width='300' alt='終了画面' src=https://user-images.githubusercontent.com/117723810/216196638-f732a076-e99d-4ab0-8fde-4aaf5cfda275.png>
<image width='500' alt='終了後のメイン画面' src=https://user-images.githubusercontent.com/117723810/216196653-908d8816-05f0-4789-bdb0-1817348da661.png>



### 処理速度の目安
1秒あたりのチャットデータ取得数 \
約110 ~ 130

試用環境 \
OS : Windows11 \
CPU: Core i7 \
通信速度: 約 100 Mbs



## お問い合わせ
質問や要望などありましたら気軽にご連絡ください。 \
mail: suzucd02@gmail.com \
twitter:@suzu20439071 \
Github: suzu02



# License
LC Manager is licensed under the MIT license. \
Copyright &copy; 2023, suzu
