# coding=utf-8
from flask import (
    request,
    redirect,
    session,
    url_for,
    render_template,
    flash,
    jsonify,
    current_app,
    send_from_directory,
)
from datetime import datetime, timedelta
import os
from flask_login import login_required, current_user
from . import main
from ..database import DatabasePool, execute_query
from .. import login_manager
from ..models import User
import pytz
import time

# 设置图片上传路径
IMAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "main/static/images"
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main.route("/index", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")


@main.errorhandler(403)
def page_not_found(e):
    return render_template("404.html"), 403


def get_date_range(time_range):
    """根据时间范围参数计算日期范围的辅助函数"""
    now = datetime.now()
    end_date = now

    if time_range == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == "yesterday":
        start_date = (now - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == "week":
        start_date = now - timedelta(days=7)
    elif time_range == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    return start_date, end_date


def get_ShipIn_Warn_data():
    """船舶信息异常检测接口（船舶吃水，船舶尺寸）"""
    sql = "SELECT * FROM tbl_inout_result"
    return execute_query(sql)


def get_put_Into_Gear_data():
    """船舶入档推送接口"""
    sql = "SELECT * FROM tbl_inout_result"
    return execute_query(sql)


def get_out_data():
    """船舶卡口检测接口（出闸）"""
    sql = "SELECT * FROM tbl_inout_result"
    return execute_query(sql)


def get_outTime_data():
    """最后一艘船船闸中间速度"""
    sql = "SELECT * FROM tbl_inout_result"
    return execute_query(sql)


def get_allOut_data():
    """船舶出空信号接口"""
    sql = "SELECT * FROM tbl_inout_result"
    return execute_query(sql)


def get_up_gate_person_monitoring_data():
    """上游船舶进闸安全检测"""
    sql = """SELECT id,gate_id,has_person_1,has_person_2
            FROM tb_gate_person_monitoring
            WHERE gate_id = 2
            ORDER BY occur_time DESC LIMIT 1"""
    return execute_query(sql)


def get_down_gate_person_monitoring_data():
    """下游船舶进闸安全检测"""
    sql = """SELECT id,gate_id,has_person_1,has_person_2
            FROM tb_gate_person_monitoring
            WHERE gate_id = 1
            ORDER BY occur_time DESC LIMIT 1"""
    return execute_query(sql)


def get_openDoorEvent_data():
    """船舶进闸事件检测"""
    sql = """SELECT object_id,type
            FROM tbl_rope_result
            WHERE object_id = 202
            ORDER BY create_time DESC LIMIT 1"""
    return execute_query(sql)


def get_openDoorEvent_data_syy():
    sql = """SELECT object_id,type
            FROM tbl_rope_result
            WHERE object_id = 202
            ORDER BY create_time DESC LIMIT 1"""
    return execute_query(sql)


def get_openDoorEvent_data_syz():
    try:
        sql = """SELECT object_id, type, create_time
                FROM tbl_rope_result
                WHERE object_id = 201
                ORDER BY create_time DESC LIMIT 1"""
        result = execute_query(sql)
        if result:
            # 格式化时间为字符串，数据库已设置为东八区时区
            for row in result:
                if "create_time" in row and row["create_time"]:
                    row["create_time"] = row["create_time"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
        return result
    except Exception as e:
        current_app.logger.error(
            f"Database error in get_openDoorEvent_data_syz: {str(e)}"
        )
        raise


def get_openDoorEvent_data_xyy():
    sql = """SELECT object_id,type
            FROM tbl_rope_result
            WHERE object_id = 102
            ORDER BY create_time DESC LIMIT 1"""
    return execute_query(sql)


def get_openDoorEvent_data_xyz():
    sql = """SELECT object_id,type
            FROM tbl_rope_result
            WHERE object_id = 101
            ORDER BY create_time DESC LIMIT 1"""
    return execute_query(sql)


def dist_danger_data_sy():
    sql = """SELECT line_type2,dist_danger
            FROM tb_warning_monitor
            WHERE lock_id = 2
            ORDER BY occur_time DESC LIMIT 1"""
    return execute_query(sql)


def dist_danger_data_xy():
    sql = """SELECT line_type2,dist_danger
            FROM tb_warning_monitor
            WHERE lock_id = 1
            ORDER BY occur_time DESC LIMIT 1"""
    return execute_query(sql)


def gate_floating_sy():
    sql = """SELECT has_floater
            FROM tb_gate_floating_monitoring
            WHERE gate_id = 2
            ORDER BY id DESC LIMIT 1"""
    return execute_query(sql)


def gate_floating_xy():
    sql = """SELECT has_floater
            FROM tb_gate_floating_monitoring
            WHERE gate_id = 1
            ORDER BY id DESC LIMIT 1"""
    return execute_query(sql)


def change_cable_data():
    sql = """SELECT huanlan_flag
            FROM tb_mooring_security
            ORDER BY id DESC LIMIT 1"""
    return execute_query(sql)


def get_out_data_208():
    sql = """SELECT *
            FROM tbl_inout_result
            WHERE lock_id = 208
            ORDER BY id DESC LIMIT 1"""
    return execute_query(sql)


def get_out_data_210():
    sql = """SELECT *
            FROM tbl_inout_result
            WHERE lock_id = 210
            ORDER BY id DESC LIMIT 1"""
    return execute_query(sql)


def get_out_data_115():
    sql = """SELECT *
            FROM tb_gate_alignment
            WHERE lock_id = 115
            ORDER BY id DESC LIMIT 1"""
    return execute_query(sql)


def get_latest_data(currentPage=1, per_page=10):
    """获取最新的船舶数据"""
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            offset = (currentPage - 1) * per_page

            # 获取总记录数
            count_sql = "SELECT COUNT(*) as total_count FROM tbl_boat_result_114"
            count_result = execute_query(count_sql)
            if not count_result:
                return [], 0

            total_count = count_result[0]["total_count"]

            # 获取分页数据
            data_sql = """
                SELECT id, direction, name, create_time, pic1, pic2, pic3, pic4, pic5
                FROM tbl_boat_result_114
                ORDER BY create_time DESC
                LIMIT %s OFFSET %s
            """
            recent_ships = execute_query(data_sql, (per_page, offset))

            # 格式化数据
            formatted_ships = []
            for ship in recent_ships:
                # 确保时间使用正确的时区
                if isinstance(ship["create_time"], datetime):
                    local_time = (
                        ship["create_time"]
                        .replace(tzinfo=pytz.UTC)
                        .astimezone(current_app.config["TIMEZONE"])
                    )
                    time_str = local_time.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    time_str = str(ship["create_time"])

                formatted_ship = {
                    "id": ship["id"],
                    "direction": ship["direction"],
                    "name": ship["name"],
                    "create_time": time_str,
                    "images": [],
                    "pic1": ship.get("pic1", ""),
                    "pic2": ship.get("pic2", ""),
                    "pic3": ship.get("pic3", ""),
                    "pic4": ship.get("pic4", ""),
                    "pic5": ship.get("pic5", ""),
                }
                # 添加图片URL
                for i in range(1, 6):
                    pic_key = f"pic{i}"
                    if ship.get(pic_key):
                        image_url = url_for(
                            "static", filename=f"images/{ship[pic_key]}", _external=True
                        )
                        formatted_ship["images"].append(image_url)
                formatted_ships.append(formatted_ship)

            return formatted_ships, total_count

        except Exception as e:
            if attempt == max_retries - 1:
                current_app.logger.error(f"获取船舶数据失败(最后一次尝试): {str(e)}")
                return [], 0
            current_app.logger.warning(
                f"获取船舶数据失败(尝试 {attempt + 1}/{max_retries}): {str(e)}"
            )
            time.sleep(retry_delay)


@main.route("/get_history_data")
def get_history_data():
    try:
        currentPage = int(request.args.get("currentPage", 1))
        per_page = 10
        data, total_count = get_latest_data(currentPage, per_page)

        if total_count == 0:
            return jsonify(
                {
                    "code": 0,
                    "message": "暂无数据",
                    "data": [],
                    "total_pages": 0,
                    "current_page": currentPage,
                    "total_count": 0,
                }
            )

        total_pages = (total_count + per_page - 1) // per_page

        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": data,
                "total_pages": total_pages,
                "current_page": currentPage,
                "total_count": total_count,
            }
        )
    except Exception as e:
        current_app.logger.error(f"获取历史数据失败: {str(e)}")
        return jsonify(
            {
                "code": -1,
                "message": str(e),
                "data": [],
                "total_pages": 0,
                "current_page": 1,
                "total_count": 0,
            }
        )


@main.route("/query_ships", methods=["POST"])
def query_ships():
    try:
        data = request.get_json()
        sql = """SELECT id,direction,name,create_time
                FROM tbl_boat_result_114
                WHERE create_time BETWEEN %s AND %s"""
        params = [data.get("startTime"), data.get("endTime")]

        if data.get("monitorPoint"):
            sql += " AND direction = %s"
            params.append(data.get("monitorPoint"))
        if data.get("shipName"):
            sql += " AND name = %s"
            params.append(data.get("shipName"))

        result = execute_query(sql, tuple(params))
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error in query_ships: {str(e)}")
        return jsonify({"error": str(e)}), 500


@main.route("/getShipInWarn", methods=["GET"])
def getShipInWarn():
    try:
        data = get_ShipIn_Warn_data()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/putIntoGear", methods=["GET"])
def putIntoGear():
    try:
        data = get_put_Into_Gear_data()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/getOut", methods=["GET"])
def Out():
    try:
        data = get_out_data()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/getOutTime", methods=["GET"])
def OutTime():
    try:
        data = get_outTime_data()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/allOut", methods=["GET"])
def allOut():
    try:
        data = get_allOut_data()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/openDoorSafe_up", methods=["GET"])
def up_openDoorSafe():
    try:
        data = get_up_gate_person_monitoring_data()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/openDoorSafe_down", methods=["GET"])
def down_openDoorSafe():
    try:
        data = get_down_gate_person_monitoring_data()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/openDoorEvent", methods=["GET"])
def openDoorEvent():
    try:
        data = get_openDoorEvent_data_syy()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/openDoorEvent_syy", methods=["GET"])
def openDoorEvent_syy():
    try:
        data = get_openDoorEvent_data_syy()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/openDoorEvent_syz", methods=["GET"])
def openDoorEvent_syz():
    try:
        data = get_openDoorEvent_data_syz()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/openDoorEvent_xyy", methods=["GET"])
def openDoorEvent_xyy():
    try:
        data = get_openDoorEvent_data_xyy()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/openDoorEvent_xyz", methods=["GET"])
def openDoorEvent_xyz():
    try:
        data = get_openDoorEvent_data_xyz()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/dist_danger_sy", methods=["GET"])
def dist_danger_sy():
    try:
        data = dist_danger_data_sy()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/dist_danger_xy", methods=["GET"])
def dist_danger_xy():
    try:
        data = dist_danger_data_xy()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/gate_floating_monitoring_sy", methods=["GET"])
def gate_floating_monitoring_sy():
    try:
        data = gate_floating_sy()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/gate_floating_monitoring_xy", methods=["GET"])
def gate_floating_monitoring_xy():
    try:
        data = gate_floating_xy()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/change_cable", methods=["GET"])
def change_cable():
    try:
        data = change_cable_data()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/getOut208", methods=["GET"])
def Out208():
    try:
        data = get_out_data_208()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/getOut210", methods=["GET"])
def Out210():
    try:
        data = get_out_data_210()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/getOut115", methods=["GET"])
def Out115():
    try:
        data = get_out_data_115()
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/query", methods=["GET"])
def query():
    try:
        # 获取查询参数
        ship_number = request.args.get("shipNumber", "")  # 船舶编号
        time_range = request.args.get("timeRange", "today")  # 时间范围
        direction = request.args.get("direction", "")  # 点位方向
        page = int(request.args.get("page", 1))
        per_page = 10

        start_date, end_date = get_date_range(time_range)
        offset = (page - 1) * per_page

        # 构建基础查询SQL
        query = """
            SELECT id, direction, name, create_time
            FROM tbl_boat_result_114
            WHERE create_time BETWEEN %s AND %s
        """
        params = [start_date, end_date]

        # 添加船舶编号条件
        if ship_number:
            query += " AND id LIKE %s"
            params.append(f"%{ship_number}%")

        # 添加点位方向条件
        if direction:
            query += " AND direction = %s"
            params.append(direction)

        # 构建计数查询
        count_query = """
            SELECT COUNT(*) as total
            FROM tbl_boat_result_114
            WHERE create_time BETWEEN %s AND %s
        """
        count_params = [start_date, end_date]

        if ship_number:
            count_query += " AND id LIKE %s"
            count_params.append(f"%{ship_number}%")

        if direction:
            count_query += " AND direction = %s"
            count_params.append(direction)

        # 添加分页和排序
        query += " ORDER BY create_time DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        # 执行查询
        total_count = execute_query(count_query, tuple(count_params))[0]["total"]
        results = execute_query(query, tuple(params))

        # 格式化日期时间
        for row in results:
            if isinstance(row["create_time"], datetime):
                row["create_time"] = row["create_time"].strftime("%Y-%m-%d %H:%M:%S")

        total_pages = (total_count + per_page - 1) // per_page

        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": results,
                "pagination": {
                    "total_pages": total_pages,
                    "current_page": page,
                    "total_count": total_count,
                    "per_page": per_page,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
            }
        )

    except Exception as e:
        current_app.logger.error(f"查询错误: {str(e)}")
        return (
            jsonify(
                {
                    "code": -1,
                    "message": f"查询失败: {str(e)}",
                    "data": [],
                    "pagination": {
                        "total_pages": 0,
                        "current_page": 1,
                        "total_count": 0,
                        "per_page": 10,
                        "has_next": False,
                        "has_prev": False,
                    },
                }
            ),
            500,
        )


@main.route("/get_images", methods=["GET"])
def get_images():
    """获取船舶图片"""
    try:
        id = request.args.get("id")
        if not id:
            return jsonify({"code": -1, "message": "缺少ID参数", "images": []}), 400

        sql = """SELECT pic1, pic2, pic3, pic4, pic5
                FROM tbl_boat_result_114
                WHERE id = %s"""
        result = execute_query(sql, (id,))

        if not result:
            return jsonify({"code": 0, "message": "未找到相关图片", "images": []})

        images = []
        for col in ["pic1", "pic2", "pic3", "pic4", "pic5"]:
            if result[0][col]:
                image_url = url_for(
                    "static", filename=f"images/{result[0][col]}", _external=True
                )
                images.append(image_url)

        return jsonify({"code": 0, "message": "success", "images": images})
    except Exception as e:
        current_app.logger.error(f"获取图片失败: {str(e)}")
        return jsonify({"code": -1, "message": str(e), "images": []}), 500


@main.route("/images/<path:filename>")
def serve_image(filename):
    """提供图片文件服务"""
    try:
        if not os.path.exists(os.path.join(IMAGE_PATH, filename)):
            current_app.logger.error(f"图片不存在: {filename}")
            return (
                jsonify(
                    {"code": -1, "message": "图片不存在", "error": "Image not found"}
                ),
                404,
            )

        response = send_from_directory(IMAGE_PATH, filename)
        response.headers["Cache-Control"] = "public, max-age=31536000"  # 缓存一年
        return response
    except Exception as e:
        current_app.logger.error(f"提供图片服务失败: {str(e)}")
        return (
            jsonify({"code": -1, "message": str(e), "error": "Failed to serve image"}),
            500,
        )


@main.route("/get_data")
def get_data():
    """兼容旧的API路由，功能与get_history_data相同"""
    try:
        current_app.logger.info("开始处理/get_data请求")
        currentPage = int(request.args.get("currentPage", 1))
        per_page = 10
        current_app.logger.info(
            f"请求参数: currentPage={currentPage}, per_page={per_page}"
        )

        data, total_count = get_latest_data(currentPage, per_page)
        current_app.logger.info(
            f"查询结果: 数据条数={len(data)}, 总记录数={total_count}"
        )

        if total_count == 0:
            current_app.logger.info("未找到数据")
            return jsonify(
                {
                    "code": 0,
                    "message": "暂无数据",
                    "data": [],
                    "pagination": {
                        "total_pages": 0,
                        "current_page": currentPage,
                        "total_count": 0,
                        "per_page": per_page,
                        "has_next": False,
                        "has_prev": False,
                    },
                }
            )

        total_pages = (total_count + per_page - 1) // per_page
        current_app.logger.info(f"计算分页: 总页数={total_pages}")

        response_data = {
            "code": 0,
            "message": "success",
            "data": data,
            "pagination": {
                "total_pages": total_pages,
                "current_page": currentPage,
                "total_count": total_count,
                "per_page": per_page,
                "has_next": currentPage < total_pages,
                "has_prev": currentPage > 1,
            },
        }
        current_app.logger.info("请求处理完成")
        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"获取数据失败: {str(e)}")
        return jsonify(
            {
                "code": -1,
                "message": str(e),
                "data": [],
                "pagination": {
                    "total_pages": 0,
                    "current_page": 1,
                    "total_count": 0,
                    "per_page": 10,
                    "has_next": False,
                    "has_prev": False,
                },
            }
        )
