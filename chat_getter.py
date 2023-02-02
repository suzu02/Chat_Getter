import csv
import pathlib
import re
import time

import pyperclip
import PySimpleGUI as sg
import pytchat


sg.theme('DarkGrey9')
sg.set_options(
    button_color=(sg.theme_text_color(), sg.theme_input_background_color()),
    font=('Yu Gothic UI', 12),
    button_element_size=(9, 1),
    auto_size_buttons=False,
    icon='./icon.ico',
)

app_name = 'Chat Getter'
font_sm = ('Yu Gothic UI', 10)
btn_lg = (15, 1)
red = '#ff6565'
blue = '#65D8FF'
green = '#65FF65'
tips_default = '動画のURL ( ID )、保存PATHを設定した後、\n開始ボタンをクリックすると処理が開始されます。'
tips_start = 'チャットデータ取得 / CSV出力の処理を開始します。'
tips_complete = 'チャットデータ取得 / CSV出力の処理が終了しました。'
tips_cancel = 'チャットデータ取得 / CSV出力の処理を中止しました。'
tips_error = 'URL ( ID ) が無効 or 未設定箇所があります。'


def create_processing_win():
    """チャットデータ取得処理の進捗画面を生成。

    Returns:
        object: PySimpleGUI.Window

    """

    layout = [
        [sg.Text('チャットデータ取得中 ...')],
        [sg.Text(text='取得数'), sg.Text(text='0', key='-COUNT-')],
        [sg.VPush()],
        [sg.Button('中 止', font=font_sm, key='-CANCEL-')],
    ]

    return sg.Window(
        f'処理中  - {app_name} -',
        layout,
        element_justification='c',
        disable_close=True,
        finalize=True,
    )


def create_cancel_win():
    """チャットデータ取得処理の中止画面を生成。

    Returns:
        object: PySimpleGUI.Window

    """

    layout = [
        [sg.Text('本当に中止しますか？')],
        [sg.VPush()],
        [sg.Button('OK', font=font_sm), sg.Button('Cancel', font=font_sm)],
    ]

    return sg.Window(
        f'確認  - {app_name} -',
        layout,
        element_justification='c',
        modal=True,
    )


def create_complete_win(total, elapsed_time):
    """チャットデータ取得処理の終了画面を生成。

    Returns:
        object: PySimpleGUI.Window

    """
    m, s = map(int, divmod(elapsed_time, 60))
    h, m = map(int, divmod(m, 60))
    power = int(total // elapsed_time)

    result_layout = [
        [sg.Text(f'  取得総数  {total:,}  ')],
        [sg.Text(f'  経過時間  {h:02}:{m:02}:{s:02}  ')],
        [sg.Text(f'  1秒あたり取得数  {power:,} / s  ')],
    ]

    layout = [
        [sg.Text('処理終了')],
        [sg.Frame(title='', layout=result_layout, border_width=1)],
        [sg.VPush()],
        [sg.Button('戻 る', font=font_sm)],
    ]

    return sg.Window(
        f'終了  - {app_name} -',
        layout,
        element_justification='c',
    )


def extract_id(input_value):
    """動画のURLからIDを抽出する処理。

    Note:
        pytchatにURLを設定する場合、YouTubeにおける共有ボタンのURLでは例外が発生。
        よって、URLが設定された場合はIDを抽出、pytchatの処理はIDに統一。
        アドレスバーのURL形式もしくは共有ボタンのURL形式の場合だけIDを抽出。
        それ以外の場合はIDが設定されたと仮定して抽出処理は行わずにそのまま返す。

    Args:
        input_value (str): URL(ID)欄の設定値。

    Returns:
        特定の条件に合致する場合はextracted_id、それ以外の場合は引数input_valueを返す。
            extracted_id (str): 動画のURLから抽出したID。

    """
    address_bar_pattern = r'https://www.youtube.com/watch\?v='
    share_btn_pattern = r'https://www.youtube.com/live/'

    if re.match(address_bar_pattern, input_value):
        m = re.search(r'v=(?P<id>[\w\W]+)&[\w\W]+ab_channel', input_value)
        extracted_id = m.group('id')
        return extracted_id
    elif re.match(share_btn_pattern, input_value):
        m = re.search(r'live/(?P<id>[\w\W]+)\?', input_value)
        extracted_id = m.group('id')
        return extracted_id
    else:
        return input_value


def check_id(id):
    """pytchatにおける動画IDの有効/無効の確認処理

    Args:
        id (str): 確認対象の動画ID

    Returns:
        成功すれば引数id、それ以外の場合はFalseを返す。

    """
    try:
        livechat = pytchat.create(video_id=id)
        livechat.is_alive()
    # 共有ボタンのURL、ショート動画などが指定された場合は例外発生
    except pytchat.exceptions.InvalidVideoIdException:
        return False
    else:
        while livechat.is_alive():
            livechat.get()
            # 例外は発生しないが、ライブ動画、投稿動画の場合は対象外とする
            if not livechat.is_replay():
                return False
            else:
                return id


def get_chat_data(id, data_names, window):
    """チャットデータの取得処理。

    Args:
        id (str): 取得対象の動画ID。
        date_names (list): 取得するチャットデータの項目名。
        window (object): メイン画面のPySimpleGUI.Windowオブジェクト。

    Returns:
        取得終了した場合はiterable(chat_data, total)、それ以外の場合はFalseを返す。
            chat_data (list): 取得したすべてのチャットデータ。
            total (int): 取得したチャットデータの総数。

    """
    processing_win = create_processing_win()
    processing_win.minimize()
    total = 0
    # 最終的にCSV出力処理に渡すリスト
    chat_data = []

    # video_idを渡してpytchatのインスタンス生成
    livechat = pytchat.create(video_id=id)
    # アーカイブ動画の場合はチャットデータが無くなるまでループ
    while livechat.is_alive():
        # チャットデータを取得(1回の取得で約30~40件)
        chatdata = livechat.get()
        # 取得したチャットデータから指定した項目を順番に取り出す
        for c in chatdata.items:
            # 1件分のチャットデータを一時保存するdict
            inner = {}
            total += 1
            inner[data_names[0]] = total
            inner[data_names[1]] = c.datetime
            inner[data_names[2]] = c.elapsedTime
            inner[data_names[3]] = c.author.name
            inner[data_names[4]] = c.message
            inner[data_names[5]] = c.type
            inner[data_names[6]] = c.currency
            inner[data_names[7]] = c.amountValue
            inner[data_names[8]] = c.author.channelUrl
            chat_data.append(inner)

        # 処理画面の表示
        # 短いタイムアウトを設定することで、一旦ループから抜けて以降の画面更新処理等を行う
        event, _ = processing_win.read(timeout=0)
        processing_win['-COUNT-'].update(f'{total:,}')
        if event == '-CANCEL-':
            cancel_win = create_cancel_win()
            event, _ = cancel_win.read()
            if event == 'OK':
                livechat.terminate()
                cancel_win.close()
                processing_win.close()
                return False
            else:
                cancel_win.close()

    processing_win.close()
    return chat_data, total


def save_csv(data, fieldnames, path):
    """CSVファイルの出力処理。

    Args:
        data (list): 出力対象のデータ。
        fieldnames (list): CSVファイルのヘッダー名。
        path (str): 出力時の保存パス。

    """
    with open(path, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames)
        writer.writeheader()
        writer.writerows(data)


def start_event(window, values):
    """STARTイベント発生時の各処理を管理。

    Args:
        window (object): メイン画面のPySimpleGUI.Windowオブジェクト。
        values (dict): メイン画面の設定値。

    """
    # 前段階として、メイン画面の設定値 / CSVのヘッダー名の変数定義
    input_url = values['-INPUT_URL-'].replace(' ', '')
    input_path = pathlib.Path(values['-INPUT_PATH-'])
    data_names = [
        'num', 'd_time', 'e_time', 'name', 'message', 'type', 'unit',
        'amount', 'channel'
    ]

    # 初めに設定値の有無を確認
    if not input_url or not input_path:
        window['-TIPS-'].update(tips_error, text_color=red)
    else:
        # ID抽出処理 / IDの確認処理 実行
        temporary_id = extract_id(input_url)
        confirm_id = check_id(temporary_id)

        if not confirm_id:
            window['-TIPS-'].update(tips_error, text_color=red)
        # IDの確認処理が成功した場合
        else:
            # メイン画面の情報変更 / 非表示
            window['-TIPS-'].update(tips_start, text_color=green)
            sg.popup_notify(
                '処理画面に切り替わります。',
                title='処理開始',
                fade_in_duration=150,
                display_duration_in_ms=1400,
            )
            window.hide()
            # 処理時間の計測開始
            start_time = time.time()
            # チャットデータ取得処理 実行 / 処理画面の表示
            result = get_chat_data(confirm_id, data_names, window)
            # 取得処理をキャンセルした場合はその時点でSTARTイベント終了
            if not result:
                window['-TIPS-'].update(tips_cancel, text_color=red)
                window.un_hide()
                return
            chat_data, total = result
            # CSV保存処理 実行
            save_csv(chat_data, data_names, input_path)
            # 処理時間計測終了 / 経過時間の算出
            end_time = time.time()
            elapsed_time = end_time - start_time
            # 終了画面の表示
            complete_win = create_complete_win(total, elapsed_time)
            complete_win.read()
            complete_win.close()
            # メイン画面の情報変更 / 再表示
            window['-INPUT_URL-'].update('')
            window['-INPUT_PATH-'].update('')
            window['-TIPS-'].update(tips_complete, text_color=blue)
            window.un_hide()


def main():
    """メイン画面のループ処理"""
    layout = [
        [
            sg.Text('URL ( ID )', size=(8, 1), key='-TEXT_URL-'),
            sg.Input(
                '',
                size=(25, 1),
                pad=((5, 0), (15, 0)),
                right_click_menu=[
                    '&input', ['&コピー', '&切り取り', '&貼り付け', '&削除'],
                ],
                background_color=sg.theme_background_color(),
                key='-INPUT_URL-',
            ),
            sg.Button(
                'クリア',
                font=font_sm,
                size=(8, 1),
                pad=((0, 5), (15, 0)),
                key='-CLEAR-',
            )
        ],
        [
            sg.Text('保存PATH', size=(8, 1), key='-TEXT_PATH-'),
            sg.Input(
                '',
                size=(25, 1),
                disabled=True,
                disabled_readonly_background_color=(
                    sg.theme_background_color()),
                pad=((5, 0), (15, 0)),
                key='-INPUT_PATH-',
            ),
            sg.FileSaveAs(
                '選択',
                target='-INPUT_PATH-',
                font=font_sm,
                size=(8, 1),
                pad=((0, 5), (15, 0)),
                file_types=(('CSV Files', '*.csv'),),
                key='-SELECT-',
            ),
        ],
        [
            sg.Frame(
                'Tips',
                font=font_sm,
                expand_x=True,
                border_width=1,
                layout=[[sg.T(tips_default, pad=(5, (0, 5)), key='-TIPS-')]],
            )
        ],
        [
            sg.Push(),
            sg.Button('開  始', font=font_sm, size=btn_lg, key='-START-'),
            sg.Button('終  了', font=font_sm, size=btn_lg, key='-QUIT-'),
        ],
        [sg.VPush()],
    ]

    window = sg.Window(
        app_name,
        layout,
        grab_anywhere=True,
        element_padding=(5, (15, 0)),
    )

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, '-QUIT-'):
            break

        if event == '-START-':
            start_event(window, values)

        if event == '-CLEAR-':
            window['-INPUT_URL-'].update('')

        if event == 'コピー':
            pyperclip.copy(values['-INPUT_URL-'])
        elif event == '切り取り':
            pyperclip.copy(values['-INPUT_URL-'])
            window['-INPUT_URL-'].update('')
        elif event == '貼り付け':
            window['-INPUT_URL-'].update(pyperclip.paste())
        elif event == '削除':
            window['-INPUT_URL-'].update('')

    window.close()


if __name__ == '__main__':
    main()
