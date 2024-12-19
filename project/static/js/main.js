        // 原有的JavaScript代码保持不变
        // ...
        // 建立WebSocket连接
        const socket = io();
        
        // 初始化船舶数据
        const ships = [
            {name: "华海徐州", x: 10, y: 10},
            {name: "鲁济宁6021", x: 120, y: 10},
            {name: "江海长顺", x: 230, y: 10},
            {name: "红桥628", x: 340, y: 10},
            {name: "远宁998", x: 10, y: 50},
            {name: "滨海001", x: 120, y: 50},
            {name: "南浮567", x: 230, y: 50},
            {name: "海启879", x: 340, y: 50}
        ];

        // 创建船舶按钮
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

        // 更新时间显示
        function updateDateTime() {
            const now = new Date();
            const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
            const formatted = `${now.getFullYear()}/${(now.getMonth()+1).toString().padStart(2,'0')}/${now.getDate().toString().padStart(2,'0')} ${days[now.getDay()]} ${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}`;
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
                        position: {x: currentX, y: currentY}
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
        socket.on('update_database', function(data) {
            // Get reference to the correct table
            const tbody = document.querySelector('#shipTable3 tbody');
            if (!tbody) return;

            // Clear existing table content
            tbody.innerHTML = '';

            // Add only the first 10 rows of data
            data.slice(0, 10).forEach((row, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${row.id || ''}</td>
                    <td>${row.direction || ''}</td>
                    <td>${row.create_time || ''}</td>
                    <td>${row.name || ''}</td>
                    <td>${row.status || ''}</td>
                    <td><button onclick="showDetails('${row.name || ''}')">查看详情</button></td>
                `;
                tbody.appendChild(tr);
            });
        });


        // 处理接收到的船舶更新数据
        socket.on('update_ship', function(data) {
            const button = Array.from(document.getElementsByClassName('ship-button'))
                               .find(btn => btn.textContent === data.ship_name);
            
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
                updateTable(data);
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

        // 更新表格
        function updateTable(data) {
            const tbody = document.querySelector('#shipTable tbody');
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${tbody.children.length + 1}</td>
                <td>${Date.now().toString().slice(-3)}</td>
                <td>实时位置更新</td>
                <td>${data.timestamp}</td>
                <td>${data.ship_name}</td>
                <td>${data.status}</td>
                <td><button onclick="showDetails('${data.ship_name}')">查看详情</button></td>
            `;
            
            tbody.insertBefore(row, tbody.firstChild);
            
            // 保持最多显示10行
            while (tbody.children.length > 10) {
                tbody.removeChild(tbody.lastChild);
            }
        }
        function updateTable_database(data) {
            const tbody = document.querySelector('#shipTable2 tbody');
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${tbody.children.length + 1}</td>
                <td>${Date.now().toString().slice(-3)}</td>
                <td>实时位置更新</td>
                <td>${data.timestamp}</td>
                <td>${data.ship_name}</td>
                <td>${data.status}</td>
                <td><button onclick="showDetails('${data.ship_name}')">查看详情</button></td>
            `;
            
            tbody.insertBefore(row, tbody.firstChild);
            
            // 保持最多显示10行
            while (tbody.children.length > 10) {
                tbody.removeChild(tbody.lastChild);
            }
        }

        // 显示详情
        function showDetails(shipName) {
            alert(`显示 ${shipName} 的详细信息`);
        }

        // 添加Tab切换功能
        function switchTab(tabId) {
            // 隐藏所有tab内容
            const tabContents = document.getElementsByClassName('tab-content');
            for (let content of tabContents) {
                content.classList.remove('active');
            }
            
            // 取消所有tab按钮的激活状态
            const tabButtons = document.getElementsByClassName('tab-button');
            for (let button of tabButtons) {
                button.classList.remove('active');
            }
            
            // 显示选中的tab内容
            document.getElementById(tabId).classList.add('active');
            
            // 激活对应的tab按钮
            event.target.classList.add('active');
        }
        


        // 原有的初始化代码
        createShipButtons();
        setInterval(updateDateTime, 1000);
        updateDateTime();
