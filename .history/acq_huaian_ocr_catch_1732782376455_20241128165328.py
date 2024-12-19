import logging
from paddleocr import PaddleOCR

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 初始化 PaddleOCR
logger.debug("Initializing PaddleOCR...")
ocr4model = PaddleOCR(
    det_model_dir='./inference/ch_PP-OCRv4_det_server_infer/',
    rec_model_dir='./inference/ch_PP-OCRv4_rec_server_infer/',
    use_angle_cls=True,
    lang='ch'
)
logger.debug("PaddleOCR initialized successfully.")

# 测试 OCR 功能
def test_ocr(image_path):
    logger.debug(f"Processing image: {image_path}")
    # start_time = time.time()
    result = ocr4model.ocr(image_path, det=True, cls=True)
    # end_time = time.time()
    logger.debug(f"OCR result: {result}")
    logger.debug(f"Total elapsed time: {end_time - start_time:.2f} seconds")
    return result

# 示例图像路径
image_path = "D:\Project\ship_data240\ID001_20241128_154403_239_666.jpg"

# 调用测试函数
test_ocr(image_path)