async function fetchSystemInfo() {
    const progress = document.getElementById('loading-progress');

    try {
        progress.style.display = 'block';
        const response = await fetch('https://example.com');//填写你的后端监测地址
        const data = await response.json();

        document.getElementById('cpu-usage').textContent = data.cpu.usage;
        document.getElementById('cpu-count').textContent = data.cpu.count;

        document.getElementById('memory-usage').textContent = data.memory.usage;
        document.getElementById('memory-total').textContent = data.memory.total;
        document.getElementById('memory-used').textContent = data.memory.used;

        document.getElementById('disk-usage').textContent = data.disk.usage;
        document.getElementById('disk-total').textContent = data.disk.total;
        document.getElementById('disk-used').textContent = data.disk.used;

        document.getElementById('uptime-days').textContent = data.uptime_days;

        let tempsText = '';
        for (const [name, entries] of Object.entries(data.temps)) {
            tempsText += `${name}:\n`;
            entries.forEach(entry => {
                tempsText += `    ${entry.label || name}: ${entry.current} °C (最高温度 = ${entry.high}, 临界温度 = ${entry.critical})\n`;
            });
        }
        document.getElementById('temps').textContent = tempsText;

        document.getElementById('net-sent').textContent = data.network.sent;
        document.getElementById('net-recv').textContent = data.network.recv;

        const processesTable = document.getElementById('processes');
        processesTable.innerHTML = '';
        data.processes.forEach(proc => {
            const row = `<tr>
            <td>${proc.pid}</td>
            <td>${proc.name}</td>
            <td>${proc.cpu_percent}</td>
            </tr>`;
            processesTable.innerHTML += row;
        });

        let fansText = '';
        for (const [name, entries] of Object.entries(data.fan_speeds)) {
            fansText += `${name}:\n`;
            entries.forEach(entry => {
                fansText += `    ${entry.label}: ${entry.speed} RPM\n`;
            });
        }
        document.getElementById('fans').textContent = fansText;

        let voltagesText = '';
        for (const [name, entries] of Object.entries(data.voltages)) {
            voltagesText += `${name}:\n`;
            entries.forEach(entry => {
                voltagesText += `    ${entry.label}: ${entry.voltage} V\n`;
            });
        }
        document.getElementById('voltages').textContent = voltagesText;
    } catch (error) {
        console.error('Error fetching system info:', error);
    } finally {
        progress.style.display = 'none';
    }
}

setInterval(fetchSystemInfo, 4000);//获取数据的等待时间
fetchSystemInfo();
