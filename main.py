from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from PIL import Image, ImageTk
from Image_compress import jpeg

root = Tk()
root.title("JPEG壓縮實作")
root.geometry("1280x720")
root.resizable(False, False)
img_id = 0
path = str()
image_raw = str()
image_compressed = str()
ratio = 0
JPEG = jpeg()


def open_image():
    global path, image_raw
    path = askopenfilename(title="選擇圖片")
    img = Image.open(path)
    resolution = img.width / img.height
    if resolution < 1:
        image_raw = ImageTk.PhotoImage(img.resize((int(400 * resolution), 400)))
    else:
        image_raw = ImageTk.PhotoImage(img.resize((400, int(400 / resolution))))
    before_img.config(image=image_raw)
    selected_label.config(text="已選擇圖片：{}".format(path.split("/")[-1]))


def set_ratio():
    global ratio
    ratio = int(ratio_ent.get())
    compress_ratio.config(text="當前壓縮比：{}".format(ratio))


def compress_image():
    global image_compressed, ratio
    JPEG.set_image(filename=path)
    JPEG.encode(ratio=ratio / 100)
    JPEG.decode()

    img = JPEG.get_compressed_img()
    resolution = img.width / img.height
    if resolution < 1:
        image_compressed = ImageTk.PhotoImage(img.resize((int(400 * resolution), 400)))
    else:
        image_compressed = ImageTk.PhotoImage(img.resize((400, int(400 / resolution))))
    after_img.config(image=image_compressed)

    MSE_label.config(text="MSE:{:.3f}".format(JPEG.get_MSE()))


def save_file():
    global img_id
    files = [('24位元點陣圖', '*.bmp')]
    try:
        file = asksaveasfilename(filetypes=files, initialfile="Compressed_{}.bmp".format(img_id))
        img_id += 1
        JPEG.get_compressed_img().save(file)

    except AttributeError:
        showwarning("錯誤", "請先執行壓縮")
        pass
    except ValueError:
        pass


Label(root, text="Step 1：", font="Helvetic 20").place(x=10, y=506)
Label(root, text="Step 2：", font="Helvetic 20").place(x=10, y=586)
Label(root, text="Step 3：", font="Helvetic 20").place(x=10, y=666)
Button(root, text="選擇圖片", font="Helvetic 20", command=open_image, width=16).place(x=100, y=500)
Button(root, text="設定壓縮比(0~100)", font="Helvetic 20", command=set_ratio, width=16).place(x=100, y=580)
Button(root, text="壓縮", font="Helvetic 20", command=compress_image, width=16).place(x=100, y=660)
Button(root, text="存檔", font="Helvetic 20", command=save_file, width=16).place(x=350, y=660)
Label(root, text="壓縮前圖片", font="Helvetic 25").place(x=30, y=10)
Label(root, text="壓縮後圖片", font="Helvetic 25").place(x=670, y=10)

selected_label = Label(root, text="已選擇圖片：", font="Helvetic 20")
compress_ratio = Label(root, text="當前壓縮比：80（預設）", font="Helvetic 20")
MSE_label = Label(root, text="MSE：", font="Helvetic 20")
ratio_ent = Entry(root, font="Helvetic 20", width=3)
before_img = Label(root)
after_img = Label(root)

selected_label.place(x=670, y=506)
compress_ratio.place(x=670, y=586)
MSE_label.place(x=670, y=666)
ratio_ent.insert(0, "80")
ratio_ent.place(x=350, y=586)
after_img.place(x=670, y=50)
before_img.place(x=30, y=50)
root.mainloop()
