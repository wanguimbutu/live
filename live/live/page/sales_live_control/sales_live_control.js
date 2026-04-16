frappe.pages['sales-live-control'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Sales Live Control',
        single_column: true,
    });

    // Inject styles
    $('<style>').text(`
        .slc-root { padding: 24px; max-width: 1200px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        .slc-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .slc-title { font-size: 1.4rem; font-weight: 700; color: #0f172a; margin: 0; }
        .slc-refresh { padding: 8px 18px; background: #1d4ed8; color: #fff; border: none; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer; }
        .slc-refresh:hover { background: #1e40af; }
        .slc-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin-bottom: 24px; }
        .stat-card { background: #fff; border: 1px solid #f1f5f9; border-radius: 14px; padding: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
        .stat-value { font-size: 2rem; font-weight: 800; color: #0f172a; margin: 0 0 4px; }
        .stat-label { font-size: 0.75rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; }
        .slc-grid { display: grid; grid-template-columns: 1fr 380px; gap: 20px; margin-bottom: 24px; }
        @media (max-width: 900px) { .slc-grid { grid-template-columns: 1fr; } }
        .slc-map-card { background: #fff; border-radius: 16px; border: 1px solid #f1f5f9; box-shadow: 0 1px 8px rgba(0,0,0,0.05); overflow: hidden; }
        .slc-card-header { padding: 14px 18px; border-bottom: 1px solid #f8fafc; font-weight: 700; font-size: 0.9rem; color: #374151; }
        #slc-map { height: 380px; width: 100%; }
        .user-list { overflow-y: auto; max-height: 380px; }
        .user-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-bottom: 1px solid #f8fafc; }
        .user-item:last-child { border-bottom: none; }
        .user-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
        .dot-online { background: #22c55e; box-shadow: 0 0 0 3px rgba(34,197,94,0.2); }
        .dot-offline { background: #cbd5e1; }
        .user-info { flex: 1; min-width: 0; }
        .user-name { font-weight: 600; font-size: 0.875rem; color: #1e293b; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .user-meta { font-size: 0.72rem; color: #94a3b8; margin: 2px 0 0; }
        .battery-bar { width: 36px; height: 18px; border: 1.5px solid #e2e8f0; border-radius: 4px; position: relative; overflow: hidden; flex-shrink: 0; }
        .battery-fill { height: 100%; border-radius: 2px; transition: width 0.3s; }
        .battery-text { font-size: 0.65rem; font-weight: 700; color: #475569; position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
        .slc-checkins-card { background: #fff; border-radius: 16px; border: 1px solid #f1f5f9; box-shadow: 0 1px 8px rgba(0,0,0,0.05); overflow: hidden; }
        .checkin-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
        .checkin-table th { text-align: left; padding: 10px 16px; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 0.68rem; letter-spacing: 0.05em; border-bottom: 1px solid #f1f5f9; }
        .checkin-table td { padding: 10px 16px; border-bottom: 1px solid #f8fafc; color: #374151; vertical-align: middle; }
        .checkin-table tr:last-child td { border-bottom: none; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 0.68rem; font-weight: 700; }
        .badge-in { background: #dcfce7; color: #166534; }
        .badge-out { background: #fee2e2; color: #991b1b; }
        .slc-loading { text-align: center; padding: 60px; color: #94a3b8; font-size: 0.9rem; }
        .slc-error { text-align: center; padding: 40px; color: #dc2626; font-size: 0.9rem; }
    `).appendTo('head');

    var $body = $('<div class="slc-root">').appendTo(page.main);
    $body.html('<div class="slc-loading">Loading control panel…</div>');

    // Load Leaflet from CDN then init
    frappe.require([
        'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
        'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
    ], function() {
        loadData();
    });

    var map = null;
    var markers = {};

    function loadData() {
        frappe.call({
            method: 'live.api.presence.get_all_presence',
            callback: function(r) {
                if (r.exc) {
                    $body.html('<div class="slc-error">Failed to load data. Make sure you have System Manager role.</div>');
                    return;
                }
                renderDashboard(r.message);
            }
        });
    }

    function renderDashboard(data) {
        var presence = data.presence || [];
        var checkins = data.checkins || [];

        var online = presence.filter(function(p) { return p.online; });
        var withLocation = presence.filter(function(p) { return p.latitude && p.longitude; });
        var charging = presence.filter(function(p) { return p.is_charging; });
        var lowBattery = presence.filter(function(p) { return p.battery_level > 0 && p.battery_level <= 20; });

        $body.html(
            '<div class="slc-header">' +
                '<h1 class="slc-title">Sales Live Control Panel</h1>' +
                '<button class="slc-refresh" id="slc-refresh-btn">Refresh</button>' +
            '</div>' +
            '<div class="slc-stats">' +
                statCard(presence.length, 'Total Users') +
                statCard(online.length, 'Online Now') +
                statCard(withLocation.length, 'With Location') +
                statCard(charging.length, 'Charging') +
                statCard(lowBattery.length, 'Low Battery') +
            '</div>' +
            '<div class="slc-grid">' +
                '<div class="slc-map-card">' +
                    '<div class="slc-card-header">Live Map</div>' +
                    '<div id="slc-map"></div>' +
                '</div>' +
                '<div class="slc-map-card">' +
                    '<div class="slc-card-header">Field Team</div>' +
                    '<div class="user-list" id="slc-user-list">' +
                        buildUserList(presence) +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="slc-checkins-card">' +
                '<div class="slc-card-header">Recent Check-Ins / Check-Outs</div>' +
                buildCheckinsTable(checkins) +
            '</div>'
        );

        $('#slc-refresh-btn').on('click', function() {
            $body.find('.slc-stats').css('opacity', '0.5');
            loadData();
        });

        // Init map
        if (map) {
            map.remove();
            map = null;
            markers = {};
        }
        map = L.map('slc-map').setView([0, 20], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);

        var bounds = [];
        presence.forEach(function(p) {
            if (!p.latitude || !p.longitude) return;
            var lat = parseFloat(p.latitude);
            var lng = parseFloat(p.longitude);
            var color = p.online ? '#22c55e' : '#94a3b8';
            var battery = p.battery_level ? p.battery_level + '%' : '';
            var icon = L.divIcon({
                html: '<div style="width:14px;height:14px;border-radius:50%;background:' + color + ';border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3)"></div>',
                iconSize: [14, 14],
                iconAnchor: [7, 7],
                className: '',
            });
            var marker = L.marker([lat, lng], { icon: icon });
            var lastSeen = p.last_seen ? new Date(p.last_seen).toLocaleString() : 'Unknown';
            marker.bindPopup(
                '<strong>' + (p.full_name || p.user) + '</strong><br>' +
                '<span style="color:' + (p.online ? '#16a34a' : '#64748b') + '">' + (p.online ? 'Online' : 'Offline') + '</span><br>' +
                (battery ? 'Battery: ' + battery + (p.is_charging ? ' ⚡' : '') + '<br>' : '') +
                'Last seen: ' + lastSeen
            );
            marker.addTo(map);
            markers[p.user] = marker;
            bounds.push([lat, lng]);
        });

        if (bounds.length > 0) {
            map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
        }

        // Click user to pan to them
        $(document).on('click', '.user-item[data-user]', function() {
            var user = $(this).data('user');
            if (markers[user]) {
                markers[user].openPopup();
                map.setView(markers[user].getLatLng(), 14);
            }
        });
    }

    function statCard(value, label) {
        return '<div class="stat-card"><p class="stat-value">' + value + '</p><p class="stat-label">' + label + '</p></div>';
    }

    function buildUserList(presence) {
        if (!presence.length) return '<div style="padding:24px;text-align:center;color:#94a3b8;font-size:0.85rem;">No users found</div>';
        return presence.map(function(p) {
            var lastSeen = p.last_seen ? timeAgo(new Date(p.last_seen)) : 'Never';
            var battery = '';
            if (p.battery_level) {
                var pct = Math.min(100, Math.max(0, p.battery_level));
                var fillColor = pct > 50 ? '#22c55e' : pct > 20 ? '#f59e0b' : '#ef4444';
                battery = '<div class="battery-bar"><div class="battery-fill" style="width:' + pct + '%;background:' + fillColor + '"></div>' +
                    '<span class="battery-text">' + pct + (p.is_charging ? '⚡' : '') + '</span></div>';
            }
            return '<div class="user-item" data-user="' + p.user + '" style="cursor:pointer">' +
                '<div class="user-dot ' + (p.online ? 'dot-online' : 'dot-offline') + '"></div>' +
                '<div class="user-info">' +
                    '<p class="user-name">' + (p.full_name || p.user) + '</p>' +
                    '<p class="user-meta">' + (p.online ? 'Online' : 'Last: ' + lastSeen) + '</p>' +
                '</div>' +
                battery +
            '</div>';
        }).join('');
    }

    function buildCheckinsTable(checkins) {
        if (!checkins.length) return '<div style="padding:24px;text-align:center;color:#94a3b8;font-size:0.85rem;">No check-ins recorded</div>';
        var rows = checkins.map(function(c) {
            var time = c.time ? new Date(c.time).toLocaleString() : '—';
            var loc = (c.latitude && c.longitude) ? parseFloat(c.latitude).toFixed(4) + ', ' + parseFloat(c.longitude).toFixed(4) : '—';
            return '<tr>' +
                '<td>' + (c.employee_name || c.employee || '—') + '</td>' +
                '<td><span class="badge ' + (c.log_type === 'IN' ? 'badge-in' : 'badge-out') + '">' + (c.log_type || '—') + '</span></td>' +
                '<td>' + time + '</td>' +
                '<td>' + loc + '</td>' +
            '</tr>';
        }).join('');
        return '<table class="checkin-table"><thead><tr><th>Employee</th><th>Type</th><th>Time</th><th>Location</th></tr></thead><tbody>' + rows + '</tbody></table>';
    }

    function timeAgo(date) {
        var secs = Math.floor((new Date() - date) / 1000);
        if (secs < 60) return 'just now';
        if (secs < 3600) return Math.floor(secs / 60) + 'm ago';
        if (secs < 86400) return Math.floor(secs / 3600) + 'h ago';
        return Math.floor(secs / 86400) + 'd ago';
    }
};
