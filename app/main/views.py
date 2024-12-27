# coding=utf-8
from flask import Flask, request, redirect, session,url_for,render_template,flash,jsonify
from app import app
import pymysql
import time
import socket
from app.decorators import admin_required,permission_required
from app.models import Permission
from app.models import User
from flask_login import login_required,LoginManager,login_user,UserMixin,logout_user,current_user
from .. import login_manager
from . import main


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/index',methods=['GET','POST'])
def index():
    return render_template('index.html')


@main.errorhandler(403)
def page_not_found(e):
    return render_template('404.html'), 403

def connect_to_database():
    # 连接数据库
    connection = pymysql.connect(
        host="139.196.173.89",
        user="root",
        password="hasf12345",
        database="jiance",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
        # charset='utf8mb4',
    )
    return connection

@main.route("/get_history_data")
def get_history_data():
    try:
        currentPage = int(request.args.get("currentPage", 1))
        per_page = 10
        connection = connect_to_database()
        data, total_count = get_latest_data(connection, currentPage, per_page)
        total_pages = (total_count + per_page - 1) // per_page
        return jsonify({"data": data, "total_pages": total_pages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@main.route("/query_history", methods=["POST"])
def query_history():
    try:
        data = request.get_json()
        connection = connect_to_database()
        # 实现查询逻辑
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()


@main.route("/get_images", methods=["GET"])
def get_images():
    id = request.args.get("id")
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT pic1, pic2, pic3 FROM tbl_boat_result_114 WHERE id = %s"""
            cursor.execute(sql, (id,))
            result = cursor.fetchone()

        if result:
            images = [result[col] for col in ["pic1", "pic2", "pic3"] if result[col]]
            return jsonify({"images": images})
        else:
            return jsonify({"images": []}), 404
    finally:
        connection.close()


@main.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_PATH, filename)


@main.route("/query_ships", methods=["POST"])
def query_ships():
    data = request.get_json()
    startTime = data.get("startTime")
    endTime = data.get("endTime")
    monitorPoint = data.get("monitorPoint")
    shipName = data.get("shipName")
    connection = connect_to_database()

    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT id,direction,name,create_time FROM tbl_boat_result_114 WHERE create_time BETWEEN '{startTime}' AND '{endTime}'"""
            if monitorPoint:
                sql += f" AND direction = '{monitorPoint}'"
            if shipName:
                sql += f" AND name = '{shipName}'"
            cursor.execute(sql)
            result = cursor.fetchall()
            return jsonify(result)
    except Exception as e:
        print(f"Error querying data: {e}")
        return jsonify({"error": str(e)})


# tbl_inout_result 船舶信息异常检测接口（船舶吃水，船舶尺寸）
def get_ShipIn_Warn_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/getShipInWarn", methods=["GET"])
def getShipInWarn():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_ShipIn_Warn_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()





# tbl_inout_result 船舶入档推送接口
def get_put_Into_Gear_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/putIntoGear", methods=["GET"])
def putIntoGear():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_put_Into_Gear_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


# tbl_inout_result 船舶卡口检测接口（出闸）
def get_out_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/getOut", methods=["GET"])
def Out():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_out_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()



# tbl_inout_result 最后一艘船船闸中间速度
def get_outTime_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            out_time = cursor.fetchall()
            # connection.close()
            return out_time
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/getOutTime", methods=["GET"])
def OutTime():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_outTime_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()





# tbl_inout_result 船舶出空信号接口
def get_allOut_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result"""
            cursor.execute(sql)
            person_monitoring = cursor.fetchall()
            # connection.close()
            return person_monitoring
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/allOut", methods=["GET"])
def allOut():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_allOut_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()




# tb_gate_person_monitoring 船舶进闸安全检测接口（行人识别，漂浮物识别，超警戒线识别）
def get_up_gate_person_monitoring_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT id,gate_id,has_person_1,has_person_2 FROM tb_gate_person_monitoring WHERE gate_id = 2 ORDER BY occur_time DESC LIMIT 1"""
            cursor.execute(sql)
            up_person_monitoring = cursor.fetchall()
            # connection.close()
            return up_person_monitoring
    except Exception as e:
        print(f"Error inserting data: {e}")


def get_down_gate_person_monitoring_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT id,gate_id,has_person_1,has_person_2 FROM tb_gate_person_monitoring WHERE gate_id = 1 ORDER BY occur_time DESC LIMIT 1"""
            cursor.execute(sql)
            down_person_monitoring = cursor.fetchall()
            # connection.close()
            return down_person_monitoring
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/openDoorSafe_up", methods=["GET"])
def up_openDoorSafe():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_up_gate_person_monitoring_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


@main.route("/openDoorSafe_down", methods=["GET"])
def down_openDoorSafe():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_down_gate_person_monitoring_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()





# tb_mooring_security tbl_rope_result 船舶进闸事件检测接口
def get_openDoorEvent_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 202 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/openDoorEvent", methods=["GET"])
def openDoorEvent():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_syy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()





# tbl_boat_result
def get_latest_data(connection, currentPage=1, per_page=10):
    try:
        offset = (currentPage - 1) * per_page
        # 查询最近的十艘船记录
        with connection.cursor() as cursor:
            sql = f"""SELECT COUNT(*) as total_count FROM tbl_boat_result_114"""
            cursor.execute(sql)
            total_count = cursor.fetchone()["total_count"]
            sql = f"""SELECT id,direction,name,create_time FROM tbl_boat_result_114 ORDER BY create_time DESC LIMIT {per_page} OFFSET {offset}"""
            cursor.execute(sql)
            recent_ships = cursor.fetchall()
            # connection.close()
            return recent_ships, total_count
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/get_data", methods=["GET"])
def get_data():
    try:
        currentPage = int(request.args.get("currentPage", 1))
        per_page = 10
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data, total_count = get_latest_data(connection, currentPage, per_page)
        total_pages = (total_count + per_page - 1) // per_page  # 计算总页数
        return jsonify({"data": data, "total_pages": total_pages})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_openDoorEvent_data_syy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 202 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/openDoorEvent_syy", methods=["GET"])
def openDoorEvent_syy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_syy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_openDoorEvent_data_syz(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 201 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/openDoorEvent_syz", methods=["GET"])
def openDoorEvent_syz():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_syz(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_openDoorEvent_data_xyy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 102 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/openDoorEvent_xyy", methods=["GET"])
def openDoorEvent_xyy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_xyy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_openDoorEvent_data_xyz(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT object_id,type FROM tbl_rope_result WHERE object_id = 101 ORDER BY create_time DESC LIMIT 1"""
            cursor.execute(sql)
            rope_result = cursor.fetchall()
            # connection.close()
            return rope_result
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/openDoorEvent_xyz", methods=["GET"])
def openDoorEvent_xyz():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_openDoorEvent_data_xyz(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def dist_danger_data_sy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT line_type2,dist_danger FROM tb_warning_monitor WHERE lock_id = 2 ORDER BY occur_time DESC LIMIT 1"""
            cursor.execute(sql)
            dist_danger = cursor.fetchall()
            # connection.close()
            return dist_danger
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/dist_danger_sy", methods=["GET"])
def dist_danger_sy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = dist_danger_data_sy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def dist_danger_data_xy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT line_type2,dist_danger FROM tb_warning_monitor WHERE lock_id = 1 ORDER BY occur_time DESC LIMIT 1"""
            cursor.execute(sql)
            dist_danger = cursor.fetchall()
            # connection.close()
            return dist_danger
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/dist_danger_xy", methods=["GET"])
def dist_danger_xy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = dist_danger_data_xy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def gate_floating_sy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT has_floater FROM tb_gate_floating_monitoring WHERE gate_id = 2 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            floating = cursor.fetchall()
            # connection.close()
            return floating
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/gate_floating_monitoring_sy", methods=["GET"])
def gate_floating_monitoring_sy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = gate_floating_sy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def gate_floating_xy(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT has_floater FROM tb_gate_floating_monitoring WHERE gate_id = 1 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            floating = cursor.fetchall()
            # connection.close()
            return floating
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/gate_floating_monitoring_xy", methods=["GET"])
def gate_floating_monitoring_xy():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = gate_floating_xy(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def change_cable_data(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT huanlan_flag FROM tb_mooring_security ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            cable = cursor.fetchall()
            # connection.close()
            return cable
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/change_cable", methods=["GET"])
def change_cable():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = change_cable_data(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


def get_out_data_208(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result WHERE lock_id = 208 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/getOut208", methods=["GET"])
def Out208():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_out_data_208(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


#   检测上游是否出空
def get_out_data_210(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tbl_inout_result WHERE lock_id = 210 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/getOut210", methods=["GET"])
def Out210():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_out_data_210(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()


#   检测下游闸门是否对中
def get_out_data_115(connection):
    try:
        with connection.cursor() as cursor:
            sql = f"""SELECT * FROM tb_gate_alignment WHERE lock_id = 115 ORDER BY id DESC LIMIT 1"""
            cursor.execute(sql)
            out = cursor.fetchall()
            # connection.close()
            return out
    except Exception as e:
        print(f"Error inserting data: {e}")


@main.route("/getOut115", methods=["GET"])
def Out115():
    try:
        # 创建数据库连接
        connection = connect_to_database()
        # 获取最新数据
        data = get_out_data_115(connection)
        return jsonify({"data": data})
    except Exception as e:
        # 返回错误信息
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保无论是否发生异常，都关闭数据库连接
        if "connection" in locals() and connection is not None:
            connection.close()

