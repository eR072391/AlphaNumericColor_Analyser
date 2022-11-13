import tkinter
import pyautogui  # 外部ライブラリ
from PIL import Image, ImageTk  # 外部ライブラリ
from PIL import ImageGrab # スクリーンショット用ライブラリ
import pyocr
import numpy as np
import PIL.ImageDraw
import os


# #Pah設定
# TESSERACT_PATH = 'C:\\Users\\・・・・\\Tesseract-OCR' #インストールしたTesseract-OCRのpath
# TESSDATA_PATH = 'C:\\Users\\・・・・\\Tesseract-OCR\\tessdata' #tessdataのpath

# os.environ["PATH"] += os.pathsep + TESSERACT_PATH
# os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH


class Color:
    RED = '\033[31m'#(文字)赤
    GREEN  = '\033[32m'#(文字)緑
    BLUE = '\033[34m'#(文字)青
    YELLOW = '\033[33m'#(文字)黄
    RESET  = '\033[0m'#全てリセット

alphanumeric = {"A":0,"B":0,"C":0,"D":0,"E":0,"F":0,"G":0,"H":0,"I":0,"J":0,"K":0,"L":0,"M":0,"N":0,
                "O":0,"P":0,"Q":0,"R":0,"S":0,"T":0,"U":0,"V":0,"W":0,"X":0,"Y":0,"Z":0,
                "0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0
                }

color_flag = {"red":0,"green":0,"blue":0}

RESIZE_RETIO = 2 # 縮小倍率の規定

# ドラッグ開始した時のイベント - - - - - - - - - - - - - - - - - - - - - - - - - - 
def start_point_get(event):
    global start_x, start_y # グローバル変数に書き込みを行なうため宣言

    canvas1.delete("rect1")  # すでに"rect1"タグの図形があれば削除

    # canvas1上に四角形を描画（rectangleは矩形の意味）
    canvas1.create_rectangle(event.x,
                            event.y,
                            event.x + 1,
                            event.y + 1,
                            outline="red",
                            tag="rect1")
    # グローバル変数に座標を格納
    start_x, start_y = event.x, event.y

# ドラッグ中のイベント - - - - - - - - - - - - - - - - - - - - - - - - - - 
def rect_drawing(event):

    # ドラッグ中のマウスポインタが領域外に出た時の処理
    if event.x < 0:
        end_x = 0
    else:
        end_x = min(img_resized.width, event.x)
    if event.y < 0:
        end_y = 0
    else:
        end_y = min(img_resized.height, event.y)

    # "rect1"タグの画像を再描画
    canvas1.coords("rect1", start_x, start_y, end_x, end_y)

# ドラッグを離したときのイベント - - - - - - - - - - - - - - - - - - - - - - - - - - 
def release_action(event):

    # "rect1"タグの画像の座標を元の縮尺に戻して取得
    start_x, start_y, end_x, end_y = [
        round(n * RESIZE_RETIO) for n in canvas1.coords("rect1")
    ]

    # 取得した座標を表示
    pyautogui.alert("start_x : " + str(start_x) + "\n" + "start_y : " +
                    str(start_y) + "\n" + "end_x : " + str(end_x) + "\n" +
                    "end_y : " + str(end_y))
    
    # OKをクリックで画面を閉じる
    root.destroy()
    ImageGrab.grab(bbox=(start_x, start_y, end_x, end_y)).save("position.png")
    with open('./config.ini', mode='w') as f:
        f.write(str(start_x) + '\n')
        f.write(str(start_y) + '\n')
        f.write(str(end_x) + '\n')
        f.write(str(end_y))


def position_main(position):
    # 表示する画像の取得（スクリーンショット)
    global img
    img = pyautogui.screenshot()
    # スクリーンショットした画像は表示しきれないので画像リサイズ
    global img_resized
    img_resized = img.resize(size=(int(img.width / RESIZE_RETIO),
                                int(img.height / RESIZE_RETIO)),
                            resample=Image.BILINEAR)
    
    # img_resized = img.resize(size=(int(img.width),
    #                             int(img.height)),
    #                         resample=Image.BILINEAR)
    
    global root
    root = tkinter.Tk()
    root.attributes("-topmost", True) # tkinterウィンドウを常に最前面に表示

    # tkinterで表示できるように画像変換
    global img_tk
    img_tk = ImageTk.PhotoImage(img_resized)

    # Canvasウィジェットの描画
    global canvas1
    canvas1 = tkinter.Canvas(root,
                            bg="black",
                            width=img_resized.width,
                            height=img_resized.height)
    # Canvasウィジェットに取得した画像を描画
    canvas1.create_image(0, 0, image=img_tk, anchor=tkinter.NW)

    # Canvasウィジェットを配置し、各種イベントを設定
    canvas1.pack()
    canvas1.bind("<ButtonPress-1>", start_point_get)
    canvas1.bind("<Button1-Motion>", rect_drawing)
    canvas1.bind("<ButtonRelease-1>", release_action)

    root.mainloop()

def analysis_alphanumeric():
    img_data = Image.open('./position.png')
    
    tools = pyocr.get_available_tools()
    tool = tools[0]
    
    builder = pyocr.builders.TextBuilder(tesseract_layout=4)
    text = tool.image_to_string(img_data, lang="eng", builder=builder)
    print(Color.YELLOW + "***解析結果***" + Color.RESET)
    print("「" + text + "」")
    for i in list(text):
        try:
            tmp = alphanumeric[i.upper()]
            tmp += 1
            alphanumeric[i.upper()] = tmp
        except:
            pass
    
    for i in alphanumeric:
        if alphanumeric[i] != 0:
            print(Color.GREEN + i + ":" + Color.RESET, Color.YELLOW + str(alphanumeric[i]) + Color.RESET)
    
    print(Color.YELLOW + "************" + Color.RESET)
    
    
    # root2 = tkinter.Tk()
    # root2.attributes("-topmost", True) # tkinterウィンドウを常に最前面に表示
    
    # root2.title('test')
    # root2.mainloop()

def analysis_color():
    img_data = 'position.png'
    source = PIL.Image.open(img_data)

    small_img = source.resize((100, 100))  # 時間短縮のために解像度を落とす
    color_arr = np.array(small_img)
    w_size, h_size, n_color = color_arr.shape
    color_arr = color_arr.reshape(w_size * h_size, n_color)

    color_mean = np.mean(color_arr, axis=0)
    color_mean = color_mean.astype(int)
    color_mean = tuple(color_mean)
    
    print(color_mean)
    if color_mean[0] > color_mean[1] and color_mean[0] > color_mean[2]:
        color_flag["red"] = 1
        print(Color.RED + "赤です" + Color.RESET)
    elif color_mean[1] > color_mean[0] and color_mean[1] > color_mean[2]:
        color_flag["green"] = 1
        print(Color.GREEN + "緑です" + Color.RESET)
    else:
        color_flag["blue"] = 1
        print(Color.BLUE + "青です" + Color.RESET)
        


def main():
    position = [[0 for i in range(4)] for j in range(9)]    #範囲指定用リスト型初期化
    #position = [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]
    
    print(Color.GREEN + "*** 英数字判別処理 ***" + Color.RESET)
    for i in range(8):
        print(Color.YELLOW + "英数字判別用範囲選択",i+1,"を開始するには「y」を、" + Color.RESET)
        flag = input(Color.YELLOW + "前回の座標で行うにはそのままEnterキーを入力してください。" + Color.RESET)
        if flag.lower() == "y":
            position_main(position)
        else:
            with open('./config.ini') as f:
                start_x = int(f.readline())
                start_y = int(f.readline())
                end_x = int(f.readline())
                end_y = int(f.readline())
            ImageGrab.grab(bbox=(start_x, start_y, end_x, end_y)).save("position.png")
        
        analysis_alphanumeric()
    
    print(Color.GREEN + "*** 色判別処理 ***" + Color.RESET)
    print(Color.YELLOW + "色彩判別用範囲選択を開始するには、" + Color.RESET)
    input(Color.YELLOW + "Enterキーを入力してください" + Color.RESET)
    position_main(position)
    
    analysis_color()

if __name__ == "__main__":
    banner = """
    _    _  __    _    __  _  __    ___   ___   ___ 
  .' \  / |/ /  .' \  / / | |/,'  ,' _/  / _/  / o |
 / o / / || /  / o / / /_ | ,'   _\ `.  / _/  /  ,' 
/_n_/ /_/|_/  /_n_/ /___//_/    /___,' /___/ /_/`_\ 
                                                    
"""
    print(banner)
    main()
