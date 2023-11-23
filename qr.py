# import modules
import qrcode
from PIL import Image

# taking image which user wants
# in the QR code center
Logo_link = 'owl.jpg'

logo = Image.open(Logo_link)

# taking base width
basewidth = 25

# adjust image size
wpercent = (basewidth/float(logo.size[0]))
hsize = int((float(logo.size[1])*float(wpercent)))
logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
QRcode = qrcode.QRCode(
	error_correction=qrcode.constants.ERROR_CORRECT_H
)

# taking url or text
#url = 'https://www.lorenzoreyes.dev/'
url = 'https://api.whatsapp.com/send?phone=5492477562603&text=hola'
# adding URL or text to QRcode
QRcode.add_data(url)

# generating QR code
QRcode.make()

# taking color name from user
QRcolor = 'Blue'

# adding color to QR code
QRimg = QRcode.make_image(
	fill_color=QRcolor, back_color="white").convert('RGB')

# set size of QR code
#pos = ((QRimg.size[0] - logo.size[0]) // 2,
#	(QRimg.size[1] - logo.size[1]) // 2)
#QRimg.paste(logo, pos)

# save the QR code generated
QRimg.save('lorenzo_QR.png')

print('QR code generated!')
