// 初始化Socket.IO客户端
var socket = io();

// 从模板中获取初始的 currentPage 和 totalPages
var currentPage = {{ currentPage }};
var totalPages = {{ totalPages }};

// Tab切换功能
document.addEventListener('DOMContentLoaded', function () {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有活动状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.style.display = 'none');

            // 激活当前tab
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            const currentTab = document.getElementById(`${tabId}-tab`);
            currentTab.style.display = 'block';

            // 如果切换到历史记录标签，更新表格数据
            if (tabId === 'history') {
                updateHistoryTable(1);
            }
        });
    });

    // 初始化显示主页
    document.getElementById('main-tab').style.display = 'block';
});

function createShipButtons() {
    const container = document.getElementById('shipContainer');
    ships.forEach(ship => {
        const button = document.createElement('button');
        button.className = 'ship-button';
        button.textContent = ship.name;
        button.style.left = ship.x + 'px';
        button.style.top = ship.y + 'px';

        const statusIndicator = document.createElement('div');
        statusIndicator.className = 'status-indicator';
        button.appendChild(statusIndicator);

        container.appendChild(button);
        setupDragListeners(button);
    });
}




// 从模板中获取初始的 currentPage 和 totalPages
var currentPage = {{ currentPage }};
var totalPages = {{ totalPages }};

// 模拟船舶数据，实际应用中应从服务器获取
const ships = [
    { name: "远宁998", x: 10, y: 10, status: "正常" },
    { name: "运沙船", x: 10, y: 80, status: "警告" }
];

function createShipButtons() {
    const container = document.getElementById('shipContainer');
    ships.forEach(ship => {
        const button = document.createElement('button');
        button.className = 'ship-button';
        button.textContent = ship.name;
        button.style.left = ship.x + 'px';
        button.style.top = ship.y + 'px';

        const statusIndicator = document.createElement('div');
        statusIndicator.className = 'status-indicator';
        button.appendChild(statusIndicator);

        container.appendChild(button);
        setupDragListeners(button);
    });
}



// 下游出空检测
function createxychukong() {
    setInterval(() => {
        fetch('/getOut208')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('xy_chukong');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].type == 0 ? '#28a745' : '#dc3545';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 上游出空检测
function createsychukong() {
    setInterval(() => {
        fetch('/getOut210')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('sy_chukong');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].type == 0 ? '#28a745' : '#dc3545';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 下游对中检测
function createxyduizhong() {
    setInterval(() => {
        fetch('/getOut115')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('xy_duizhong');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].status == 1 ? '#28a745' : '#dc3545';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 上游人员检测
function createOpenDoorSafeUpButtons() {
    setInterval(() => {
        fetch('/openDoorSafe_up')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('openDoorSafe_Upstream');
                if (button && data.data && data.data.length > 0) {
                    const person = data.data[0];
                    const color = (person.has_person_1 == 1 || person.has_person_2 == 1) ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 下游人员检测
function createOpenDoorSafeDownButtons() {
    setInterval(() => {
        fetch('/openDoorSafe_down')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('openDoorSafe_Downstream');
                if (button && data.data && data.data.length > 0) {
                    const person = data.data[0];
                    const color = (person.has_person_1 == 1 || person.has_person_2 == 1) ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 上游右系缆识别
function create_syy_xilanButtons() {
    setInterval(() => {
        fetch('/openDoorEvent_syy')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('syy_xilan');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].type == 0 ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 上游左系缆识别
function create_syz_xilanButtons() {
    setInterval(() => {
        fetch('/openDoorEvent_syz')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('syz_xilan');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].type == 0 ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 下游右系缆识别
function create_xyy_xilanButtons() {
    setInterval(() => {
        fetch('/openDoorEvent_xyy')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('xyy_xilan');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].type == 0 ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 下游左系缆识别
function create_xyz_xilanButtons() {
    setInterval(() => {
        fetch('/openDoorEvent_xyz')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('xyz_xilan');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].type == 0 ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 上游超警戒线检测
function createdangerdatasyButtons() {
    setInterval(() => {
        fetch('/dist_danger_sy')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('sy_jingjie');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].dist_danger == 0 ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 下游超警戒线检测
function createdangerdataxyButtons() {
    setInterval(() => {
        fetch('/dist_danger_xy')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('xy_jingjie');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].dist_danger == 0 ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 上游漂浮物检测
function create_floating_Buttons_sy() {
    setInterval(() => {
        fetch('/gate_floating_monitoring_sy')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('sy_piaofuwu');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].has_floater == 1 ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 下游漂浮物检测
function create_floating_Buttons_xy() {
    setInterval(() => {
        fetch('/gate_floating_monitoring_xy')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('xy_piaofuwu');
                if (button && data.data && data.data.length > 0) {
                    const color = data.data[0].has_floater == 1 ? '#dc3545' : '#28a745';
                    button.style.setProperty('background-color', color, 'important');
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 换缆提醒
function create_cable_Buttons() {
    setInterval(() => {
        fetch('/change_cable')
            .then(response => response.json())
            .then(data => {
                const button = document.getElementById('huanlan');
                if (button && data.data && data.data.length > 0) {
                    if (data.data[0].huanlan_flag == 1) {
                        button.style.setProperty('background-color', '#dc3545', 'important');
                        setTimeout(() => {
                            button.style.setProperty('background-color', '#28a745', 'important');
                        }, 300000);
                    } else {
                        button.style.setProperty('background-color', '#28a745', 'important');
                    }
                }
            })
            .catch(error => console.error('Error:', error));
    }, 5000);
}

// 更新时间显示
function updateDateTime() {
    const now = new Date();
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    const formatted = `${now.getFullYear()}/${(now.getMonth() + 1).toString().padStart(2, '0')}/${now.getDate().toString().padStart(2, '0')} ${days[now.getDay()]} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    document.getElementById('datetime').textContent = formatted;
}

// 设置拖拽监听器
function setupDragListeners(button) {
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    button.addEventListener('mousedown', dragStart);
    button.addEventListener('mousemove', drag);
    button.addEventListener('mouseup', dragEnd);
    button.addEventListener('mouseleave', dragEnd);

    function dragStart(e) {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;

        if (e.target === button) {
            isDragging = true;
            button.classList.add('dragging');
        }
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;

            xOffset = currentX;
            yOffset = currentY;

            const container = document.getElementById('shipContainer');
            const containerRect = container.getBoundingClientRect();

            const buttonRect = button.getBoundingClientRect();
            const maxX = containerRect.width - buttonRect.width;
            const maxY = containerRect.height - buttonRect.height;

            currentX = Math.max(0, Math.min(currentX, maxX));
            currentY = Math.max(0, Math.min(currentY, maxY));

            button.style.left = currentX + 'px';
            button.style.top = currentY + 'px';

            // 发送位置更新到服务器
            socket.emit('position_update', {
                ship_name: button.textContent,
                position: { x: currentX, y: currentY }
            });
        }
    }

    function dragEnd() {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
        button.classList.remove('dragging');
    }
}

// 处理接收到的船舶更新数据
socket.on('update_ship', function (data) {
    const button = Array.from(document.getElementsByClassName('ship-button')).find(btn => btn.textContent === data.ship_name);

    if (button) {
        // 更新位置
        if (data.position) {
            button.style.left = data.position.x + 'px';
            button.style.top = data.position.y + 'px';
        }

        // 更新状态指示器
        const indicator = button.querySelector('.status-indicator');
        if (indicator) {
            indicator.className = 'status-indicator status-' + data.status.toLowerCase();
        }

        // 更新信息面板
        updateInfoPanel(data);

        // 更新表格
        // updateTable(data);
        updateTable(1);
    }
});

// 更新信息面板
function updateInfoPanel(data) {
    const panel = document.getElementById('infoPanel');
    const info = document.getElementById('shipInfo');

    info.innerHTML = `
                <p>船名: ${data.ship_name}</p>
                <p>状态: ${data.status}</p>
                <p>更新时间: ${data.timestamp}</p>
            `;

    panel.style.display = 'block';
    setTimeout(() => panel.style.display = 'none', 3000);
}

function updateTable(currentPage) {
    currentPage = currentPage || 1;
    fetch('/get_data?currentPage=' + currentPage)
        .then(response => response.json())
        .then(data => {
            if (!data || !Array.isArray(data.data)) {
                console.error('Invalid data format:', data);
                return;
            }

            totalPages = data.total_pages;
            const tbody = document.querySelector('#shipTable tbody');
            tbody.innerHTML = '';
            data.data.forEach((row, index) => {
                const tr = document.createElement('tr');
                const fields = ['id', 'name', 'direction', 'create_time', 'ship_number', 'status'];
                fields.forEach(fieldName => {
                    const td = document.createElement('td');
                    td.textContent = row[fieldName] || ''; // 使用 || '' 处理可能不存在的字段
                    tr.appendChild(td);
                });

                // 添加最后一列“打开详情”
                const detailTd = document.createElement('td');
                const detailLink = document.createElement('button');
                detailLink.textContent = '详情';
                detailLink.dataset.id = row.id; // 保存单元格序号到数据属性
                detailLink.addEventListener('click', () => openDetailModal(detailLink.dataset.id));
                detailTd.appendChild(detailLink);
                tr.appendChild(detailTd);
                tbody.appendChild(tr);
            });
            addPaginationButtons(totalPages, currentPage);
        })
        .catch(error => console.error('Error fetching data:', error));
}

// 显示详情
function showDetails(shipName) {
    alert(`显示 ${shipName} 的详细信息`);
}

let originalImages = [];
function openDetailModal(id) {
    fetch(`/get_images?id=${id}`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('detailModal');
            const swiperWrapper = modal.querySelector('.swiper-wrapper');
            swiperWrapper.innerHTML = ''; // 清空现有内容

            // 添加图片到轮播
            data.images.forEach(imageUrl => {
                const slide = document.createElement('div');
                slide.className = 'swiper-slide';

                const img = document.createElement('img');
                img.src = '/static/images/Snipaste_2024-12-06_14-55-18.png';
                img.style.maxWidth = '100%';
                img.style.height = 'auto';

                slide.appendChild(img);
                swiperWrapper.appendChild(slide);
            });

            // 初始化Swiper
            if (window.mySwiper) {
                window.mySwiper.destroy(true, true);
            }

            window.mySwiper = new Swiper('.swiper-container', {
                loop: true,
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
            });

            modal.style.display = 'block';
        })
        .catch(error => console.error('Error:', error));
}

function closeModal() {
    const modal = document.getElementById('detailModal');
    if (window.mySwiper) {
        window.mySwiper.destroy(true, true);
    }
    modal.style.display = 'none';
}

// 确保事件监听器正确设置
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('detailModal');
    const closeButton = document.querySelector('.close-button');

    closeButton.onclick = closeModal;

    window.onclick = function (event) {
        if (event.target === modal) {
            closeModal();
        }
    }
});

// 添加分页按钮
const paginationContainer = document.createElement('div');
paginationContainer.className = 'pagination';
document.body.appendChild(paginationContainer);

function addPaginationButtons(totalPages, currentPage) {
    const paginationContainer = document.getElementById('mainPagination');
    paginationContainer.innerHTML = '';

    // 第一页/共多少页
    const pageInfo = document.createElement('span');
    pageInfo.textContent = `第 ${currentPage} 页 / 共 ${totalPages} 页`;
    paginationContainer.appendChild(pageInfo);

    // 首页按钮
    const firstButton = document.createElement('button');
    firstButton.textContent = '首页 ';
    firstButton.disabled = currentPage === 1;
    firstButton.addEventListener('click', () => {
        if (currentPage !== 1) {
            currentPage = 1;
            updateTable(currentPage);
            addPaginationButtons(totalPages, currentPage);
        }
    });

    paginationContainer.appendChild(firstButton);

    // 上一页按钮
    const prevButton = document.createElement('button');
    prevButton.textContent = '上一页 ';
    prevButton.disabled = currentPage === 1;
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            updateTable(currentPage);
            addPaginationButtons(totalPages, currentPage);
        }
    });
    paginationContainer.appendChild(prevButton);

    // 下一页按钮
    const nextButton = document.createElement('button');
    nextButton.textContent = '下一页 ';
    nextButton.disabled = currentPage === totalPages;
    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            updateTable(currentPage);
            addPaginationButtons(totalPages, currentPage);
        }
    });
    paginationContainer.appendChild(nextButton);

    // 尾页按钮
    const lastButton = document.createElement('button');
    lastButton.textContent = '尾页 ';
    lastButton.disabled = currentPage === totalPages;
    lastButton.addEventListener('click', () => {
        if (currentPage !== totalPages) {
            currentPage = totalPages;
            updateTable(currentPage);
            addPaginationButtons(totalPages, currentPage);
        }
    });
    paginationContainer.appendChild(lastButton);

    // 跳转输入框
    const gotoInput = document.createElement('input');
    gotoInput.type = 'number';
    gotoInput.min = 1;
    gotoInput.max = totalPages;
    gotoInput.value = currentPage;
    gotoInput.addEventListener('change', () => {
        const pageNumber = parseInt(gotoInput.value, 10);
        if (pageNumber >= 1 && pageNumber <= totalPages) {
            currentPage = pageNumber;
            updateTable(currentPage);
            addPaginationButtons(totalPages, currentPage);
        }
    });
    paginationContainer.appendChild(gotoInput);

    // 跳转按钮
    const gotoButton = document.createElement('button');
    gotoButton.textContent = '跳转 ';
    gotoButton.addEventListener('click', () => {
        const pageNumber = parseInt(gotoInput.value, 10);
        if (pageNumber >= 1 && pageNumber <= totalPages) {
            currentPage = pageNumber;
            updateTable(currentPage);
            addPaginationButtons(totalPages, currentPage);
        }
    });
    paginationContainer.appendChild(gotoButton);
}



// 新增历史记录相关函数
function updateHistoryTable(currentPage) {
    fetch('/get_history_data?currentPage=' + currentPage)
        .then(response => response.json())
        .then(data => {
            if (!data || !Array.isArray(data.data)) {
                console.error('Invalid data format:', data);
                return;
            }
            const tbody = document.querySelector('#historyShipTable tbody');
            tbody.innerHTML = '';
            data.data.forEach(row => {
                const tr = document.createElement('tr');
                const fields = ['id', 'name', 'direction', 'create_time', 'ship_number', 'status'];
                fields.forEach(fieldName => {
                    const td = document.createElement('td');
                    td.textContent = row[fieldName] || '';
                    tr.appendChild(td);
                });

                const detailTd = document.createElement('td');
                const detailLink = document.createElement('button');
                detailLink.textContent = '详情';
                detailLink.dataset.id = row.id;
                detailLink.addEventListener('click', () => openDetailModal(detailLink.dataset.id));
                detailTd.appendChild(detailLink);
                tr.appendChild(detailTd);
                tbody.appendChild(tr);
            });
            updateHistoryPagination(data.total_pages, currentPage);
        })
        .catch(error => console.error('Error:', error));
}

// 更新历史记录分页控件
function updateHistoryPagination(totalPages, currentPage) {
    const paginationContainer = document.getElementById('historyPagination');
    paginationContainer.innerHTML = '';

    // 页码信息
    const pageInfo = document.createElement('span');
    pageInfo.textContent = `第 ${currentPage} 页 / 共 ${totalPages} 页`;
    paginationContainer.appendChild(pageInfo);

    // 首页按钮
    const firstButton = document.createElement('button');
    firstButton.textContent = '首页';
    firstButton.disabled = currentPage === 1;
    firstButton.addEventListener('click', () => {
        if (currentPage !== 1) {
            updateHistoryTable(1);
        }
    });
    paginationContainer.appendChild(firstButton);

    // 上一页按钮
    const prevButton = document.createElement('button');
    prevButton.textContent = '上一页';
    prevButton.disabled = currentPage === 1;
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            updateHistoryTable(currentPage - 1);
        }
    });
    paginationContainer.appendChild(prevButton);

    // 下一页按钮
    const nextButton = document.createElement('button');
    nextButton.textContent = '下一页';
    nextButton.disabled = currentPage === totalPages;
    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            updateHistoryTable(currentPage + 1);
        }
    });
    paginationContainer.appendChild(nextButton);

    // 尾页按钮
    const lastButton = document.createElement('button');
    lastButton.textContent = '尾页';
    lastButton.disabled = currentPage === totalPages;
    lastButton.addEventListener('click', () => {
        if (currentPage !== totalPages) {
            updateHistoryTable(totalPages);
        }
    });
    paginationContainer.appendChild(lastButton);

    // 跳转输入框
    const gotoInput = document.createElement('input');
    gotoInput.type = 'number';
    gotoInput.min = 1;
    gotoInput.max = totalPages;
    gotoInput.value = currentPage;
    paginationContainer.appendChild(gotoInput);

    // 跳转按钮
    const gotoButton = document.createElement('button');
    gotoButton.textContent = '跳转';
    gotoButton.addEventListener('click', () => {
        const pageNumber = parseInt(gotoInput.value, 10);
        if (pageNumber >= 1 && pageNumber <= totalPages) {
            updateHistoryTable(pageNumber);
        }
    });
    paginationContainer.appendChild(gotoButton);
}

// 修改tab切换事件，添加历史记录数据加载
document.addEventListener('DOMContentLoaded', function () {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有活动状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.style.display = 'none');

            // 激活当前tab
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            const currentTab = document.getElementById(`${tabId}-tab`);
            currentTab.style.display = 'block';

            // 如果切换到历史记录标签，更新表格数据
            if (tabId === 'history') {
                updateHistoryTable(1);
            }
        });
    });
});
// 修改历史记录查询表单提交事件
document.getElementById('historyQueryForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const formData = {
        startTime: document.getElementById('historyStartTime').value,
        endTime: document.getElementById('historyEndTime').value,
        monitorPoint: document.getElementById('historyMonitorPoint').value,
        direction: document.getElementById('historyDirection').value,
        shipName: document.getElementById('historyShipName').value
    };

    // 发送查询请求并更新表格
    fetch('/query_history', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            updateHistoryTable(1); // 查询后显示第一页
        })
        .catch(error => console.error('Error:', error));
});

function queryHistoryData(formData) {
    fetch('/query_history', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            updateHistoryTable(1);
        })
        .catch(error => console.error('Error:', error));
}

// 确保所有初始化函数在页面加载完成后执行
createShipButtons();
createOpenDoorSafeUpButtons();
createOpenDoorSafeDownButtons();
create_syy_xilanButtons();
create_syz_xilanButtons();
create_xyy_xilanButtons();
create_xyz_xilanButtons();
createdangerdatasyButtons();
createdangerdataxyButtons();
create_floating_Buttons_sy();
create_floating_Buttons_xy();
create_cable_Buttons();
createxychukong();
createsychukong();
createxyduizhong();

updateDateTime();
setInterval(updateDateTime, 1000);

// 初始化表格数据
updateTable(1);
setInterval(() => updateTable(currentPage), 100000);

// 初始化模态框事件监听
const modal = document.getElementById('detailModal');
const closeButton = document.querySelector('.close-button');

closeButton.onclick = closeModal;
window.onclick = function (event) {
    if (event.target === modal) {
        closeModal();
    }
};