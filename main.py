from datetime import date,datetime
import mysql.connector
from mysql.connector import Error
class Nguoi():
    def __init__(self, ho_ten, cccd, so_dienthoai, tuoi, sodu0 = 0, sodu1 = 0, sodu2 = 0):
        self.ho_ten = ho_ten
        self.cccd = cccd
        self.so_dienthoai = so_dienthoai
        self.tuoi = tuoi
        self.sodu0 = sodu0
        self.sodu1 = sodu1
        self.sodu2 = sodu2
    @property
    def sodu(self):
        return self.sodu0 + self.sodu1 + self.sodu2
class GiaoDich():
    def  __init__(self, nguoi_chovay, nguoi_no, sotien, laisuat, ngay_chovay, lancuoi_capnhat = None, ghichu = ""):
        self.nguoi_chovay = nguoi_chovay
        self.nguoi_no = nguoi_no
        self.sotien = sotien
        self.laisuat = laisuat
        self.ngay_chovay = ngay_chovay
        self.ghichu = ghichu
        if lancuoi_capnhat == None:
            self.lancuoi_capnhat = ngay_chovay
        else:
            self.lancuoi_capnhat = lancuoi_capnhat
        if self.laisuat == 1:
            self.nguoi_chovay.sodu1 = self.nguoi_chovay.sodu1 + self.sotien
            self.nguoi_no.sodu1 = self.nguoi_no.sodu1 - self.sotien
        elif self.laisuat == 2:
            self.nguoi_chovay.sodu2 = self.nguoi_chovay.sodu2 + self.sotien
            self.nguoi_no.sodu2 = self.nguoi_no.sodu2 - self.sotien
        else: 
            self.nguoi_chovay.sodu0 = self.nguoi_chovay.sodu0 + self.sotien
            self.nguoi_no.sodu0 = self.nguoi_no.sodu0 - self.sotien
    def Lai_suat(self,now):
        months_diff = (now.year - self.lancuoi_capnhat.year) * 12 + (now.month - self.lancuoi_capnhat.month)
        if self.laisuat ==1:
            self.nguoi_chovay.sodu1 = self.nguoi_chovay.sodu1 - self.sotien + (self.sotien*(1.01**months_diff))//1
            self.nguoi_no.sodu1 = self.nguoi_no.sodu1 + self.sotien - (self.sotien*(1.01**months_diff))//1
            self.sotien = (self.sotien*(1.01**months_diff))//1
        elif self.laisuat == 2:
            self.nguoi_chovay.sodu2 = self.nguoi_chovay.sodu2 - self.sotien + (self.sotien*(1.02**months_diff))//1
            self.nguoi_no.sodu2 = self.nguoi_no.sodu2 + self.sotien - (self.sotien*(1.02**months_diff))//1
            self.sotien = (self.sotien*(1.02**months_diff))//1
        else:
            None
        self.lancuoi_capnhat = now
    def Thuc_hien(self):
        if self.laisuat == 1:
            self.nguoi_chovay.sodu1 = self.nguoi_chovay.sodu1 - self.sotien
            self.nguoi_no.sodu1 = self.nguoi_no.sodu1 + self.sotien
        elif self.laisuat == 2:
            self.nguoi_chovay.sodu2 = self.nguoi_chovay.sodu2 - self.sotien
            self.nguoi_no.sodu2 = self.nguoi_no.sodu2 + self.sotien
        else: 
            self.nguoi_chovay.sodu0 = self.nguoi_chovay.sodu0 - self.sotien
            self.nguoi_no.sodu0 = self.nguoi_no.sodu0 + self.sotien
            
def Nhap_nguoi():
    ten =input("Nhập tên: ")
    cccd = input("Nhập CCCD: ")
    sdt = input("Nhập số điện thoại: ")
    tuoi = int(input("Nhập tuổi: "))
    return Nguoi(ten,cccd,sdt,tuoi)
def Nhap_giaodich(lst_Nguoi,conn):
    cursor = conn.cursor()
    for i in range(len(lst_Nguoi)):
        print(lst_Nguoi[i].ho_ten,"tương ứng với số",i)
    nguoi_chovay = int(input("Nhập người cho vay: "))
    nguoi_chovay = lst_Nguoi[nguoi_chovay]
    nguoi_no = int(input("Nhập người nợ: "))
    nguoi_no = lst_Nguoi[nguoi_no]
    sotien = int(input("Nhập số tiền: "))
    laisuat = int(input("Nhập lãi suất (%): "))
    ngaychovay = input("Nhập ngày cho vay dạng YYYY/MM/DD: ")
    if ngaychovay !="":
        ngaychovay = ngaychovay.split("/")
        for i in range(len(ngaychovay)):
            ngaychovay[i] = int(ngaychovay[i])
        ngaychovay = date(ngaychovay[0],ngaychovay[1],ngaychovay[2])
    lancuoi_capnhat = input("Nhập ngày cập nhật cuối dạng YYYY/MM/DD(bỏ qua nếu lần cuối bằng ngày cho vay): ")
    if lancuoi_capnhat !="":
        lancuoi_capnhat = lancuoi_capnhat.split("/")
        for i in range(len(lancuoi_capnhat)):
            lancuoi_capnhat[i] = int(lancuoi_capnhat[i])
        lancuoi_capnhat = date(lancuoi_capnhat[0],lancuoi_capnhat[1],lancuoi_capnhat[2])
    else:
        lancuoi_capnhat = None
    ghichu = input("Nhập ghi chú (bỏ qua nếu ko cần): ")
    cursor.execute("""
        UPDATE nguoi SET sodu%s = sodu%s + %s WHERE cccd = %s
    """, (laisuat,laisuat,sotien, nguoi_chovay.cccd))

    # 5. Cập nhật số dư cho người nợ (tăng sodu1)
    cursor.execute("""
        UPDATE nguoi SET sodu%s = sodu%s - %s WHERE cccd = %s
    """, (laisuat,laisuat,sotien, nguoi_no.cccd))
    conn.commit()
    cursor.close()
    return GiaoDich(nguoi_chovay, nguoi_no, sotien, laisuat,ngaychovay,lancuoi_capnhat,ghichu)

def Capnhat_laisuat(lst_giaodich):
    now = datetime.now()
    for i in lst_giaodich:
        i.Lai_suat(now)
def Kiemtra_giaodich_trung(lst_giaodich, giaodich_moi):
    for i in lst_giaodich:
        if (giaodich_moi.nguoi_chovay == i.nguoi_chovay) and (giaodich_moi.nguoi_no == i.nguoi_no) : # Nếu khoản vay mới trùng với khoản vay cũ thì cộng vào
            i.sotien += giaodich_moi.sotien
            i.ghichu += "Đã cộng thêm "+str(giaodich_moi.sotien)+" do khoản vay trùng lặp\n"
            return True
        if (giaodich_moi.nguoi_chovay == i.nguoi_no) and (giaodich_moi.nguoi_no == i.nguoi_chovay): # Nếu khoản vay cũ có quan hệ người cũ với người mới trái ngược nhau
            if i.sotien == giaodich_moi.sotien: # Số tiền cũ và mới bằng nhau thì xóa bỏ 
                lst_giaodich.remove(i)
                print("Khoản vay mới và cũ đã dối nghịch nhau. Xóa bỏ khoản vay trước đó")
                return True
            elif i.sotien > giaodich_moi.sotien: # Số tiền cũ lớn hơn số tiền mới thì giảm bớt ở khoản vay cũ 
                i.sotien -= giaodich_moi.sotien
                i.ghichu += "Đã bỏ khoản vay mới và bỏ "+str(giaodich_moi.sotien)+" ở khoản vay cũ do khoản vay trùng lặp\n"
                return True
            else: # vì i đã có khoản cho vay nên i là chủ nợ nếu i có khoản cho vay khác thì xét ở TH 2
                lst_giaodich.remove(i)
                giaodich_moi.sotien = giaodich_moi.sotien - i.sotien
                return False
    return False # TH3 không có giao dịch cũ nào liên quan tới giao dịch mới
def In_giaodich(giaodich):
    print("Người cho vay:",giaodich.nguoi_chovay.ho_ten)
    print("Người nợ:",giaodich.nguoi_no.ho_ten)
    print("Số tiền:",giaodich.sotien,"với lãi suất",giaodich.laisuat,"%/tháng:")
    print("Ghi chú:",giaodich.ghichu) 
    print()
def In_toanbogiaodich(lst_0,lst_1,lst_2):
    for i in lst_0:
        In_giaodich(i)
    for i in lst_1:
        In_giaodich(i)
    for i in lst_2:
        In_giaodich(i)
def Timkiem_khoanno(lst_giaodich,nguoi): # hàm sẽ trả list người nợ mình với các phần từ có dạng [Số tiền, giao dịch]
    lst = []
    for i in lst_giaodich:
        if i.nguoi_chovay == nguoi:
            tmp=[]
            tmp.append(i.sotien)
            tmp.append(i)
            lst.append(tmp)
    return lst
def Timkiem_khoanvay(lst_giaodich,nguoi): # hàm sẽ trả list người cho mình vay với các phần từ có dạng [Số tiền, giao dịch]
    lst = []
    for i in lst_giaodich:
        if i.nguoi_no == nguoi:
            tmp=[]
            tmp.append(i.sotien)
            tmp.append(i)
            lst.append(tmp)
    return lst
def lay_to_hop_n(danh_sach, so_phan_tu):
    def quay_lui(bat_dau, to_hop_hien_tai):
        # Nếu tổ hợp hiện tại đạt độ dài mong muốn, thêm vào kết quả
        if len(to_hop_hien_tai) == so_phan_tu:
            ket_qua.append(to_hop_hien_tai[:])
            return
        
        # Thử thêm các phần tử từ vị trí bắt đầu trở đi
        for i in range(bat_dau, len(danh_sach)):
            to_hop_hien_tai.append(danh_sach[i])
            quay_lui(i + 1, to_hop_hien_tai)
            to_hop_hien_tai.pop()

    ket_qua = []
    # Kiểm tra điều kiện đầu vào
    if so_phan_tu < 0 or so_phan_tu > len(danh_sach):
        return ket_qua
    quay_lui(0, [])
    return ket_qua
def Timkiem_nguoicungno(lst_nguoi1,lstnguoi2):
    lst = []
    for i in lst_nguoi1:
        for j in lstnguoi2:
            if i[1].nguoi_no ==j[1].nguoi_no:
                lst.append([i,j])
    return lst
def Chuyen_giaodich(lst_giaodich, giaodich_moi,sodu_no):
    lst_nguoino_nguoino = Timkiem_khoanno(lst_giaodich, giaodich_moi.nguoi_no)
    lst_nguoino_nguoivay = Timkiem_khoanno(lst_giaodich, giaodich_moi.nguoi_chovay)
    lst_nguoicungno = Timkiem_nguoicungno(lst_nguoino_nguoivay, lst_nguoino_nguoino)
    sotien_moi = giaodich_moi.sotien 
    if sodu_no > 0: # người cho nợ có số dư lớn hơn 0 nên có thể chuyển khoản vay của mình cho thg vay
        if lst_nguoicungno !=[]: # Kiểm tra xem 2 thg cho vay với nợ thì có thằng nào nợ chung 2 thg này ko
            sum = 0
            for i in lst_nguoicungno:
                if sum + i[1][0] <=sotien_moi:
                    sum += i[1][0]
                    i[0][1].sotien += i[1][0]
                    i[0][1].ghichu += "Đã chuyển thêm "+str(i[1][0])+" do người người vay có cùng khoản nợ với "+i[0][1].ho_ten + " và "+ i[1][1].ho_ten +"\n"
                    lst_giaodich.remove(i[1][1])
                elif sum< sotien_moi:
                    i[1][1].sotien = i[1][1].sotien - sotien_moi + sum 
                    i[1][1].ghichu += "Đã chuyển bớt "+str(sotien_moi - sum)+" sang " + i[0][1].nguoi_chovay.ho_ten +" \n"
                    i[0][1].sotien += sotien_moi - sum 
                    i[0][1].nguoi_no = i[1][1].nguoi_no
                    i[0][1].ghichu += "Đã chuyển giao dịch từ " + i[0][1].nguoi_no.ho_ten +" sang\n"
                    sum =sotien_moi
                    break 
            sotien_moi = sotien_moi -sum
        if sotien_moi >0: # Chuyển từng gaio dịch của người nợ cho người vay
            lst_nguoino_nguoino = Timkiem_khoanno(lst_giaodich, giaodich_moi.nguoi_no) 
            to_hop1 = lay_to_hop_n(lst_nguoino_nguoino,1)
            for i in to_hop1: # Kiểm tra xem số tiền nợ có thể bằng tổng của 1 giao dịch của thg nợ ko
                if sotien_moi == i[0][0]:
                    i[0][1].nguoi_chovay = giaodich_moi.nguoi_chovay
                    i[0][1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_no.ho_ten +" sang\n"
                    return
            to_hop2 = lay_to_hop_n(lst_nguoino_nguoino,2)
            for i in to_hop2: # Kiểm tra xem số tiền nợ có thể bằng tổng của 2 giao dịch của thg nợ ko
                sum = i[0][0] + i[1][0]
                if sotien_moi == sum:
                    i[0][1].nguoi_chovay = giaodich_moi.nguoi_chovay
                    i[0][1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_no.ho_ten +" sang\n"
                    i[1][1].nguoi_chovay = giaodich_moi.nguoi_chovay
                    i[1][1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_no.ho_ten +" sang\n"
                    return
            sum = 0
            for i in lst_nguoino_nguoino: # Nếu ko thì chuyển lần lượt số tiền đến khi đủ 
                if sum + i[0] <= sotien_moi:
                    sum += i[0]
                    i[1].nguoi_chovay = giaodich_moi.nguoi_chovay
                    i[1].ghichu += "Đã chuyển giao dịch từ " + giaodich_moi.nguoi_no.ho_ten +" sang\n"
                elif sum <sotien_moi:
                    i[1].sotien = i[1].sotien - sotien_moi + sum 
                    i[1].ghichu += "Đã chuyển bớt "+str(sotien_moi - sum)+" sang " + giaodich_moi.nguoi_chovay.ho_ten +" \n"
                    giaodich_moi.sotien = sotien_moi - sum 
                    giaodich_moi.nguoi_no = i[1].nguoi_no
                    giaodich_moi.ghichu = "Đã chuyển giao dịch từ " + giaodich_moi.nguoi_no.ho_ten +" sang\n"
                    lst_giaodich.append(giaodich_moi)
                    break
    elif sodu_no == 0: # Trường hợp số dư thg nợ bằng 0 thì phải chuyển toàn bộ tài khoản của mình
        if lst_nguoicungno !=[]: # Kiểm tra xem 2 thg cho vay với nợ thì có thằng nào nợ chung 2 thg này ko
            sum = 0
            for i in lst_nguoicungno:
                sum += i[1][0]
                i[0][1].sotien += i[1][0]
                i[0][1].ghichu += "Đã chuyển thêm "+str(i[1][0])+" do người người vay có cùng khoản nợ với "+i[0][1].nguoi_chovay.ho_ten + " và "+ i[1][1].nguoi_chovay.ho_ten +"\n"
                lst_giaodich.remove(i[1][1])
            sotien_moi = sotien_moi -sum
        lst_nguoino_nguoino = Timkiem_khoanno(lst_giaodich, giaodich_moi.nguoi_no)
        for i in lst_nguoino_nguoino:
            i[1].nguoi_chovay = giaodich_moi.nguoi_chovay
            i[1].ghichu += "Đã chuyển giao dịch từ " + giaodich_moi.nguoi_no.ho_ten +" sang\n"
    else:
        if lst_nguoicungno !=[]: # Kiểm tra xem 2 thg cho vay với nợ thì có thằng nào nợ chung 2 thg này ko
            sum = 0
            for i in lst_nguoicungno:
                sum += i[1][0]
                i[0][1].sotien += i[1][0]
                i[0][1].ghichu += "Đã chuyển thêm "+str(i[1][0])+" do người người vay có cùng khoản nợ với "+i[0][1].nguoi_chovay.ho_ten + " và "+ i[1][1].nguoi_chovay.ho_ten +"\n"
                lst_giaodich.remove(i[1][1])
            sotien_moi = sotien_moi -sum
        lst_nguoino_nguoino = Timkiem_khoanno(lst_giaodich, giaodich_moi.nguoi_no)
        sum = 0
        for i in lst_nguoino_nguoino:
            sum+= i[1].sotien
            i[1].nguoi_chovay = giaodich_moi.nguoi_chovay
            i[1].ghichu += "Đã chuyển giao dịch từ " + giaodich_moi.nguoi_no.ho_ten +" sang\n"
        giaodich_moi.ghichu = ""
        giaodich_moi.sotien = sotien_moi - sum
        # In_giaodich(giaodich_moi)
        lst_giaodich.append(giaodich_moi)

        
def Toi_uu(lst_giaodich,giaodich_moi): 
    lst_khoanvay = Timkiem_khoanvay(lst_giaodich, giaodich_moi.nguoi_chovay)
    lst_khoanno = Timkiem_khoanno(lst_giaodich, giaodich_moi.nguoi_chovay)
    if lst_khoanvay == [] :
        return
    else:
        for i in lst_khoanno:
            lst_khoanvay = Timkiem_khoanvay(lst_giaodich, giaodich_moi.nguoi_chovay)
            for j in lst_khoanvay:
                tmp = Timkiem_khoanno(lst_giaodich, j[1].nguoi_chovay)
                for z in tmp:
                    if z[1].nguoi_no == i[1].nguoi_no: # Kiểm tra xem có trùng cái người nợ ko
                        if j[1].sotien > i[1].sotien: # Khi khoản vay lớn hơn khoản mình nợ chuyển hết khoản nợ đó 
                            z[1].sotien += i[1].sotien
                            lst_giaodich.remove(i[1])
                            j[1].sotien = j[1].sotien - i[1].sotien
                            z[1].ghichu +="Đã cộng thêm tiền do trùng lặp \n"
                        elif j[1].sotien == i[1].sotien:
                            z[1].sotien +=i[1].sotien
                            lst_giaodich.remove(i[1])
                            lst_giaodich.remove(j[1])
                            z[1].ghichu +="Đã cộng thêm tiền do trùng lặp \n"
                        else: # Khoản vay bé hơn mình chuyển hết khoản vay đó 
                            z[1].sotien += j[1].sotien
                            i[1].sotien -= j[1].sotien
                            z[1].ghichu +="Đã cộng thêm tiền do trùng lặp \n"
                            lst_giaodich.remove(j[1])
        lst_khoanno = Timkiem_khoanno(lst_giaodich, giaodich_moi.nguoi_chovay)
        tmp_lst = []
        for i in lst_khoanno:
            lst_khoanvay = Timkiem_khoanvay(lst_giaodich, giaodich_moi.nguoi_chovay)
            to_hop2 = lay_to_hop_n(lst_khoanvay,2)
            for j in to_hop2:
                sum = j[0][0] + j[1][0]
                if i[0] == sum:
                    j[0][1].nguoi_no = i[1].nguoi_no
                    j[0][1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_chovay.ho_ten +" sang\n"
                    j[1][1].nguoi_no = i[1].nguoi_no
                    j[1][1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_chovay.ho_ten +" sang\n"
                    tmp_lst.append(i[1])
                    break
        for i in tmp_lst:
            # In_giaodich(i)
            lst_giaodich.remove(i)
        tmp_lst =[]
        lst_khoanvay = Timkiem_khoanvay(lst_giaodich, giaodich_moi.nguoi_chovay)
        for i in lst_khoanvay:
            lst_khoanno = Timkiem_khoanno(lst_giaodich, giaodich_moi.nguoi_chovay)
            to_hop1 = lay_to_hop_n(lst_khoanno,1)
            for j in to_hop1: # Kiểm tra xem số tiền nợ có thể bằng tổng của 1 giao dịch của thg nợ ko
                if i[0] == j[0][0]:
                    j[0][1].nguoi_chovay = i[1].nguoi_chovay
                    j[0][1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_chovay.ho_ten +" sang\n"
                    tmp_lst.append(i[1])
                    break
            to_hop2 = lay_to_hop_n(lst_khoanno,2)
            for j in to_hop2: # Kiểm tra xem số tiền nợ có thể bằng tổng của 2 giao dịch của thg nợ ko
                sum = j[0][0] + j[1][0]
                if i[0] == sum:
                    j[0][1].nguoi_chovay = i[1].nguoi_chovay
                    j[0][1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_chovay.ho_ten +" sang\n"
                    j[1][1].nguoi_chovay = i[1].nguoi_chovay
                    j[1][1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_chovay.ho_ten +" sang\n"
                    tmp_lst.append(i[1])
                    break
            for j in lst_khoanno:
                if i[1].sotien >j[1].sotien: # Xét 1 khoản vay và khoản nợ nếu khoản vay lớn hơn thì chuyển tất khoản nợ sang và trừ đi ở khoản vay số tương ứng
                    j[1].nguoi_chovay = i[1].nguoi_chovay
                    i[1].sotien = i[1].sotien - j[1].sotien
                    j[1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_chovay.ho_ten +" sang\n"
                elif i[1].sotien == j[1].sotien:
                    j[1].nguoi_chovay = i[1].nguoi_chovay
                    tmp_lst.append(i[1])
                    j[1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_chovay.ho_ten +" sang\n"
                    break 
                else: # Nếu khoản nợ lớn hơn thì cắt khoản nợ đưa cho khoản vay
                    j[1].sotien = j[1].sotien - i[1].sotien 
                    i[1].nguoi_no = j[1].nguoi_no
                    i[1].ghichu += "Đã chuyển giao dịch của " + giaodich_moi.nguoi_chovay.ho_ten +" sang\n"
                    break
        for i in tmp_lst:
            lst_giaodich.remove(i) 

def Xu_ly(lst_0,lst_1,lst_2, giaodich_moi):
    laisuat = giaodich_moi.laisuat
    if laisuat == 1:
        sodu_no = giaodich_moi.nguoi_no.sodu1
        lst_giaodich = lst_1
    elif laisuat == 2:
        sodu_no = giaodich_moi.nguoi_no.sodu2
        lst_giaodich = lst_2
    else:
        sodu_no = giaodich_moi.nguoi_no.sodu0
        lst_giaodich = lst_0
    Capnhat_laisuat(lst_giaodich) # Tính só dư hiện tại của các giao dịch trước đó
    now = datetime.now()
    giaodich_moi.Lai_suat(now) # Để tính số dư hiện tại vì 2 khoản vay có tính lãi không thể tương tác nếu ko cùng ngày cập nhật
    if Kiemtra_giaodich_trung(lst_giaodich, giaodich_moi):
        None
    else:
        Chuyen_giaodich(lst_giaodich,giaodich_moi,sodu_no)
        Toi_uu(lst_giaodich, giaodich_moi)
def Ghi_nguoi_vaomysql(nguoi,conn):
    cursor = conn.cursor()
    sql = """
    INSERT INTO nguoi (cccd, ho_ten, so_dienthoai, tuoi, sodu0, sodu1, sodu2)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(sql, (
            nguoi.cccd,
            nguoi.ho_ten,
            nguoi.so_dienthoai,
            nguoi.tuoi,
            nguoi.sodu0,
            nguoi.sodu1,
            nguoi.sodu2
        ))
        conn.commit()
        cursor.close()
        return 0
            # print(f"Đã thêm người: {nguoi.ho_ten}")
    except mysql.connector.Error as err:
        print(f"Lỗi khi thêm người {nguoi.ho_ten}:", err)
        cursor.close()
        return 1
def Ghi_giaodich_vaomysql(lst_0,lst_1,lst_2,conn):
    lst =lst_0+lst_1+lst_2
    cursor = conn.cursor()
    sql = """
    INSERT INTO giaodich (nguoi_chovay_cccd, nguoi_no_cccd, laisuat, sotien, ngay_chovay, lancuoi_capnhat, ghichu)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for i in lst:
        try:
            cursor.execute(sql, (
                i.nguoi_chovay.cccd,
                i.nguoi_no.cccd,
                i.laisuat,
                i.sotien,
                i.ngay_chovay,
                i.lancuoi_capnhat,
                i.ghichu
            ))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Lỗi khi thêm giao dịch {i.nguoi_chovay.ho_ten}, {i.nguoi_no.ho_ten}, {i.laisuat}"+" Lỗi:\n", err)
    cursor.close()
def Xoa_toanbo_giaodich(conn):
    cursor = conn.cursor()

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("SET SQL_SAFE_UPDATES = 0")
        cursor.execute("DELETE FROM giaodich")
        cursor.execute("SET SQL_SAFE_UPDATES = 1")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")
        conn.rollback()
    finally:
        cursor.close()
def Xoa_toanboNguoi_mysql(conn):
    cursor = conn.cursor()

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("SET SQL_SAFE_UPDATES = 0")
        cursor.execute("DELETE FROM nguoi")
        cursor.execute("SET SQL_SAFE_UPDATES = 1")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")
        conn.rollback()
    finally:
        cursor.close()
def Doc_nguoi_tu_mysql(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT ho_ten, cccd, so_dienthoai, tuoi FROM nguoi")
    results = cursor.fetchall()
    danh_sach = []

    for row in results:
        ho_ten, cccd, so_dienthoai, tuoi = row
        n = Nguoi(ho_ten, cccd, so_dienthoai, tuoi)
        danh_sach.append(n)
    return danh_sach
def Doc_giaodich_tu_db(conn, lst_Nguoi):
    cursor = conn.cursor()
    # Tạo từ điển tra cứu người theo CCCD
    nguoi_dict = {n.cccd: n for n in lst_Nguoi}

    cursor.execute("SELECT nguoi_chovay_cccd, nguoi_no_cccd, sotien, laisuat, ngay_chovay, lancuoi_capnhat, ghichu FROM giaodich")
    results = cursor.fetchall()

    lst_0, lst_1, lst_2 = [], [], []

    for row in results:
        nguoi_chovay_cccd, nguoi_no_cccd, sotien, laisuat, ngay_chovay, lancuoi_capnhat, ghichu = row

        nguoi_chovay = nguoi_dict.get(nguoi_chovay_cccd)
        nguoi_no = nguoi_dict.get(nguoi_no_cccd)

        if nguoi_chovay and nguoi_no:
            gd = GiaoDich(
                nguoi_chovay=nguoi_chovay,
                nguoi_no=nguoi_no,
                sotien=sotien,
                laisuat=laisuat,
                ngay_chovay=ngay_chovay,
                lancuoi_capnhat=lancuoi_capnhat,
                ghichu=ghichu
            )
            if laisuat == 0:
                lst_0.append(gd)
            elif laisuat == 1:
                lst_1.append(gd)
            elif laisuat == 2:
                lst_2.append(gd)

    return lst_0, lst_1, lst_2
def Doc_diachisql():
    try:
        # Mở file với chế độ "a+" (đọc và ghi thêm, tạo file mới nếu không có)
        with open("address_mysql.txt", "a+") as file:
            file.seek(0)  # Di chuyển con trỏ về đầu để đọc
            lines = [line.strip() for line in file.readlines()]
            
            # Kiểm tra xem file có đủ 5 dòng không
            if len(lines) < 5:
                print("Lỗi: File address_mysql.txt không đủ thông tin kết nối (cần 5 dòng: host, user, password, database, port).")
                return 1
            
            # Lấy thông tin từ các dòng
            host, user, password, database, port = lines[:5]
            
            # Kiểm tra xem có dòng nào rỗng không
            if not all([host, user, database, port]):
                print("Lỗi: Một hoặc nhiều thông tin kết nối trong file bị rỗng.")
                return 1
            
            # Thử kết nối đến MySQL
            try:
                conn = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database,
                    port=port
                )
                if conn.is_connected():
                    print("Kết nối MySQL thành công từ file cấu hình.")
                    return conn
            except Error as e:
                print(f"Lỗi kết nối MySQL: {e}")
                return 1
                
    except Exception as e:
        print(f"Lỗi không xác định khi đọc file: {e}")
        return 1
def Ket_noisql():
    file = open("address_mysql.txt", "a+")
    file.seek(0)  # Di chuyển con trỏ về đầu file để đọc
    noidung = file.read()
    
    if noidung == "":
        print("Chưa được kết nối với MySQL, vui lòng nhập để thiết lập kết nối")
    else:
        print("Đã được kết nối với MySQL. Thông tin kết nối hiện tại:")
        file.seek(0)  # Đảm bảo đọc lại từ đầu
        lines = file.readlines()  # Đọc từng dòng
        if len(lines) >= 5:  # Kiểm tra xem file có đủ 5 dòng (host, user, password, database, port)
            host, user, password, database, port = [line.strip() for line in lines[:5]]
            print(f"Host: {host}")
            print(f"User: {user}")
            print(f"Password: {'*' * len(password)}")  # Ẩn mật khẩu
            print(f"Database: {database}")
            print(f"Port: {port}")
            
            # Kiểm tra kết nối với thông tin hiện tại
            try:
                connection = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database,
                    port=port
                )
                if connection.is_connected():
                    print("Kết nối đến MySQL vẫn hoạt động!")
                    server_info = connection.server_info
                    print(f"Phiên bản MySQL Server: {server_info}")
                    cursor = connection.cursor()
                    cursor.execute("SELECT DATABASE();")
                    db_name = cursor.fetchone()
                    print(f"Đang kết nối đến database: {db_name[0]}")
            except Error as e:
                print(f"Lỗi kết nối đến MySQL với thông tin hiện tại: {e}")
                file.close()
                return 1
            finally:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()
                    # print("Kết nối MySQL đã được đóng.")
            
            # Hỏi người dùng có muốn thay đổi kết nối không
            try:
                sign = int(input("Ấn phím 1 nếu muốn thay đổi kết nối, 0 để giữ nguyên: "))
                if sign != 1:
                    file.close()
                    return 0  # Giữ nguyên kết nối
            except ValueError:
                print("Vui lòng nhập số hợp lệ (0 hoặc 1)!")
                file.close()
                return 1

    # Nhập thông tin kết nối mới
    host = input("Nhập host: ")
    user = input("Nhập tên user: ")
    password = input("Nhập mật khẩu: ")
    database = input("Nhập tên database: ")
    port = input("Nhập port (mặc định 3306): ") or "3306"

    try:
        # Thử kết nối đến MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        
        # Nếu kết nối thành công
        if connection.is_connected():
            print("Kết nối đến MySQL thành công!")
            server_info = connection.server_info
            print(f"Phiên bản MySQL Server: {server_info}")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"Đang kết nối đến database: {db_name[0]}")

    except Error as e:
        print(f"Lỗi kết nối đến MySQL: {e}")
        file.close()
        return 1

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            # print("Kết nối MySQL đã được đóng.")

    # Ghi thông tin kết nối mới vào file
    file.seek(0)
    file.truncate()  # Xóa nội dung cũ
    print(host, file=file)
    print(user, file=file)
    print(password, file=file)
    print(database, file=file)
    print(port, file=file, end="")
    file.close()
    return 0
def Xoa_nguoi(conn,cccd_can_xoa):  
    cursor = conn.cursor()
    # Bước 1: Kiểm tra số dư của người
    cursor.execute("""
        SELECT sodu0, sodu1, sodu2 FROM nguoi WHERE cccd = %s
    """, (cccd_can_xoa,))
    row = cursor.fetchone()

    if row is None:
        print("Không tìm thấy người với CCCD đã cho.")
        return 1
    elif all(sodu == 0 for sodu in row):
        # Bước 3: Xóa người
        cursor.execute("DELETE FROM nguoi WHERE cccd = %s", (cccd_can_xoa,))
        conn.commit()
        cursor.close()
        print("Đã xóa thành công.")
        return 0
    else:
        print("Người này vẫn còn số dư:", row)
        print("Nếu vẫn muốn xóa ấn phím 1, Nếu không ấn 2 để dừng.")
        tmp = int(input("Nhập vô đây: "))
        if tmp == 1:
            cursor.execute("""
                SELECT nguoi_chovay_cccd, nguoi_no_cccd, laisuat, sotien
                FROM giaodich
                WHERE nguoi_chovay_cccd = %s OR nguoi_no_cccd = %s
            """, (cccd_can_xoa, cccd_can_xoa))

            giao_dichs = cursor.fetchall()

            for chovay_cccd, no_cccd, laisuat, sotien in giao_dichs:
                # Chọn đúng cột số dư tương ứng với lãi suất
                if laisuat == 0:
                    sodu_col = "sodu0"
                elif laisuat == 1:
                    sodu_col = "sodu1"
                elif laisuat == 2:
                    sodu_col = "sodu2"

                if chovay_cccd == cccd_can_xoa:
                    # Người đó là người cho vay → trừ tiền khỏi người nợ
                    cursor.execute(f"""
                        UPDATE nguoi SET {sodu_col} = {sodu_col} + %s WHERE cccd = %s
                    """, (sotien, no_cccd))
                elif no_cccd == cccd_can_xoa:
                    # Người đó là người nợ aaaa→ trừ tiền khỏi người cho vay
                    cursor.execute(f"""
                        UPDATE nguoi SET {sodu_col} = {sodu_col} - %s WHERE cccd = %s
                    """, (sotien,chovay_cccd))

            # 2. Xóa các giao dịch liên quan
            cursor.execute("""
                DELETE FROM giaodich WHERE nguoi_chovay_cccd = %s OR nguoi_no_cccd = %s
            """, (cccd_can_xoa, cccd_can_xoa))
            # Bước 3: Xóa người
            cursor.execute("DELETE FROM nguoi WHERE cccd = %s", (cccd_can_xoa,))
            conn.commit()
            cursor.close()
            return 0
        elif tmp == 2:
            print("Đã ngừng xóa.")
            return 1
        else:
            print("Không nhận được lệnh phù hợp. Dừng câu lệnh")
            return 1
        
def Xoa_Giaodich_Capnhat_Sodu(conn, nguoi_chovay_cccd, nguoi_no_cccd, laisuat):
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT sotien FROM giaodich
            WHERE nguoi_chovay_cccd = %s AND nguoi_no_cccd = %s AND laisuat = %s
        """, (nguoi_chovay_cccd, nguoi_no_cccd, laisuat))
        result = cursor.fetchone()

        if result is None:
            print("Không tìm thấy giao dịch để xóa.")
            return

        sotien = result[0]
        sodu_col = f"sodu{laisuat}"
        cursor.execute(f"""
            UPDATE nguoi SET {sodu_col} = {sodu_col} - %s WHERE cccd = %s
        """, (sotien, nguoi_chovay_cccd))
        cursor.execute(f"""
            UPDATE nguoi SET {sodu_col} = {sodu_col} + %s WHERE cccd = %s
        """, (sotien, nguoi_no_cccd))
        cursor.execute("""
            DELETE FROM giaodich
            WHERE nguoi_chovay_cccd = %s AND nguoi_no_cccd = %s AND laisuat = %s
        """, (nguoi_chovay_cccd, nguoi_no_cccd, laisuat))

        conn.commit()
        print("Đã xóa giao dịch và cập nhật số dư thành công.")

    except mysql.connector.Error as err:
        print(f"Lỗi MySQL: {err}")
        conn.rollback()
    finally:
        cursor.close()
def In_nguoi(lst_nguoi):
    for i in lst_nguoi:
        print("Họ và tên:",i.ho_ten," CCCD:",i.cccd,"SĐT:",i.so_dienthoai,"tuổi:",i.tuoi,"số dư:",i.sodu)
def Toi_uu_toan_bo(conn):
    lst_Nguoi = Doc_nguoi_tu_mysql(conn)
    cursor = conn.cursor()
    # Tạo từ điển tra cứu người theo CCCD
    nguoi_dict = {n.cccd: n for n in lst_Nguoi}

    cursor.execute("SELECT nguoi_chovay_cccd, nguoi_no_cccd, sotien, laisuat, ngay_chovay, lancuoi_capnhat, ghichu FROM giaodich")
    results = cursor.fetchall()

    lst_0, lst_1, lst_2 = [], [], []

    for row in results:
        nguoi_chovay_cccd, nguoi_no_cccd, sotien, laisuat, ngay_chovay, lancuoi_capnhat, ghichu = row

        nguoi_chovay = nguoi_dict.get(nguoi_chovay_cccd)
        nguoi_no = nguoi_dict.get(nguoi_no_cccd)

        if nguoi_chovay and nguoi_no:
            gd = GiaoDich(
                nguoi_chovay=nguoi_chovay,
                nguoi_no=nguoi_no,
                sotien=sotien,
                laisuat=laisuat,
                ngay_chovay=ngay_chovay,
                lancuoi_capnhat=lancuoi_capnhat,
                ghichu=ghichu
            )
            Xu_ly(lst_0,lst_1,lst_2,gd)
    Xoa_toanbo_giaodich(conn)
    Ghi_giaodich_vaomysql(lst_0,lst_1,lst_2,conn)
    cursor.close()
def main():
    conn = Doc_diachisql()
    # Xoa_toanbo_giaodich(conn)
    # Xoa_toanboNguoi_mysql(conn)
    print("Bạn muốn chức năng gì")
    print("Chức năng 1: Quản lý người ")
    print("Chức năng 2: Quản lý giao dịch")
    print("Chức năng 3: Chỉnh sửa kết nối với mysql")
    print("Chức năng 4: Tối ưu toàn bộ giao dịch")
    print("Chức năng 5: Thoát")
    choice = int(input("Nhập vào đây: "))
    if choice == 1:
        if conn == 1:
            print("Bạn chưa kết nối với sql hãy dùng chức năng 3 trước")
            return
        else:
            print("Bạn muốn chức năng gì")
            print("Chức năng 1: Thêm người ")
            print("Chức năng 2: Xóa người")
            print("Chức năng 3: In người")
            print("Chức năng 4: Thoát")
            choice1 = int(input("Nhập vào đây: "))
            if choice1 ==1:
                Nguoi_moi = Nhap_nguoi()
                Ghi_nguoi_vaomysql(Nguoi_moi, conn)
                conn.close()
                return
            elif choice1 == 2:
                cccd_muon_xoa =input("Nhập căn cước công dân bạn muốn xóa:")
                Xoa_nguoi(conn,cccd_muon_xoa)
                conn.close()
                return
            elif choice1 == 3:
                lst_Nguoi = Doc_nguoi_tu_mysql(conn)
                lst0,lst1,lst2 = Doc_giaodich_tu_db(conn,lst_Nguoi)
                In_nguoi(lst_Nguoi)
                conn.close()
                return
            else:
                conn.close()
                return
    elif choice ==2:
        if conn == 1:
            print("Bạn chưa kết nối với sql hãy dùng chức năng 3 trước")
        else:
            print("Bạn muốn chức năng gì")
            print("Chức năng 1: Thêm giao dịch ")
            print("Chức năng 2: Xóa giao dịch")
            print("Chức năng 3: Hiển thị giao dịch")
            print("Chức năng 4: Thoát")
            choice2 = int(input("Nhập vào đây: "))
            if choice2 ==1:
                lst_Nguoi = Doc_nguoi_tu_mysql(conn)
                lst0,lst1,lst2 = Doc_giaodich_tu_db(conn,lst_Nguoi)
                giaodich_moi = Nhap_giaodich(lst_Nguoi,conn) 
                Xu_ly(lst0,lst1,lst2,giaodich_moi)
                Xoa_toanbo_giaodich(conn)
                Ghi_giaodich_vaomysql(lst0, lst1, lst2, conn)
                conn.close()
                return
            elif choice2 == 2:
                # lst_Nguoi = Doc_nguoi_tu_mysql(conn)
                # lst0,lst1,lst2 = Doc_giaodich_tu_db(conn,lst_Nguoi)
                cccd_nguoi_chovay =input("Nhập căn cước công dân người cho vay:")
                cccd_nguoi_no =input("Nhập căn cước công dân người nợ:")
                laisuat = input("Nhập lãi suất của giao dịch:")
                Xoa_Giaodich_Capnhat_Sodu(conn,cccd_nguoi_chovay,cccd_nguoi_no,laisuat)
                conn.close()
                return
            elif choice2 == 3:
                lst_Nguoi = Doc_nguoi_tu_mysql(conn)
                lst0,lst1,lst2 = Doc_giaodich_tu_db(conn,lst_Nguoi)
                In_toanbogiaodich(lst0,lst1,lst2)
                conn.close
                return
            else:
                conn.close()
                return
    elif choice ==3:
        Ket_noisql()
        conn.close()
        return
    elif choice == 4:
        Toi_uu_toan_bo(conn)
        conn.close()
        return
    elif choice ==5:
        conn.close()
        return
if __name__ =="__main__":
    main()