
from osgeo import gdal
import os, time

rater_file = r"E:\Desktop\20220913-20220916\20220915\数据\2022-08-17_NJXS2DL.tif"


# 计算NDVI值
def get_ndvi(path):  # 计算某一影像的ndvi值，返回二维数组
    dataset = gdal.Open(path)
    cols = dataset.RasterXSize  # 列数
    rows = dataset.RasterYSize  # 行数

    band8 = dataset.GetRasterBand(8).ReadAsArray(0, 0, cols, rows)
    band4 = dataset.GetRasterBand(4).ReadAsArray(0, 0, cols, rows)
    molecule = band8 - band4
    denominator = band8 + band4
    del dataset
    band = molecule / denominator
    band[band > 1] = 9999  # 过滤异常值
    return band


# 输入一个日期，判断是今年的第多少天
def date_cunt(datetime1):
    """输入一个日期，判断是今年的第多少天"""
    date01 = time.mktime(time.strptime(datetime1[:4] + "0101", "%Y%m%d"))
    date02 = time.mktime(time.strptime(datetime1, "%Y%m%d"))
    cnt = (date02 - date01) / 60 / 60 / 24 + 1
    return cnt


# 玉米估产模型
# file影像路径
# date：影像时间

def Estimate_Corn(date, file):
    img_root = os.path.dirname(file)  # 获取上级目录
    # img_type = (".img", ".dat", "tiff")  # 获取影像数据类型
    driver = gdal.GetDriverByName('GTiff')  # 获取驱动
    result_name_temp = "Estimate_Corn1.tiff"  # 估产影像的名字
    result_path = os.path.join(img_root, result_name_temp)
    cunt = date_cunt(date)
    # 文件存在则删除文件
    if os.path.exists(result_path):
        os.remove(result_path)
    dataset = gdal.Open(file)
    cols = dataset.RasterXSize  # 列数
    rows = dataset.RasterYSize  # 行数
    if cunt < 115 or cunt > 278:
        print("时间参数设错误")
        return 0
    # 生成影像
    target_ds = gdal.GetDriverByName('GTiff').Create(result_path, xsize=cols, ysize=rows, bands=1,
                                                     eType=gdal.GDT_Float32)
    target_ds.SetGeoTransform(dataset.GetGeoTransform())
    target_ds.SetProjection(dataset.GetProjection())
    del dataset
    band = get_ndvi(file)
    target_ds.GetRasterBand(1).SetNoDataValue(9999)
    if 130 >= cunt:
        target_ds.GetRasterBand(1).WriteArray(band * 10000 * 0)  # 估产模型1 播种 4.25-5.10
    elif 145 >= cunt:
        target_ds.GetRasterBand(1).WriteArray(band * 10000 * 0.5654 - 9045.7)  # 估产模型2 出苗5.10-5.25
    elif 166 >= cunt:
        target_ds.GetRasterBand(1).WriteArray(band * 10000 * 0)  # 估产模型3 三叶5.25-6.15
    elif 176 >= cunt:
        target_ds.GetRasterBand(1).WriteArray(band * 10000 * 1.3128 + 2935.4)  # 估产模型4 七叶6.15-6.25
    elif 196 >= cunt:
        target_ds.GetRasterBand(1).WriteArray(band * 10000 * 2.2946 - 6263.8)  # 估产模型5 拔节 6.25-7.15
    elif 206 >= cunt:
        target_ds.GetRasterBand(1).WriteArray(band * 10000 * 0)  # 估产模型6 抽雄 7.15-7.25
    elif 217 >= cunt:
        target_ds.GetRasterBand(1).WriteArray(band * 10000 * (-2.8350) - 13692)  # 估产模型7 开花7.25-8.05
    elif 222 >= cunt:
        target_ds.GetRasterBand(1).WriteArray(band * 10000 * 0)  # 估产模型8 吐丝 8.05-8.10
    elif 253 >= cunt:
        target_ds.GetRasterBand(1).WriteArray((band * 10000 * 2.02 - 7982.5)/15)  # 估产模型9 灌浆 8.10-9.10
    elif 278 >= cunt:
        target_ds.GetRasterBand(1).WriteArray(band * 10000 * 1.9959 - 6135.4)  # 估产模型10 成熟9.10-10.05

    target_ds.FlushCache()  # 清除缓存
    if target_ds.GetRasterBand(1).ReadAsArray().all() == [0][0]:
        del target_ds
        os.remove(result_path)
        return None
    else:
        return target_ds


res = Estimate_Corn("20200817", rater_file)
