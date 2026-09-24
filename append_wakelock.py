with open('portal/templates/portal/salidas_admin_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

wakelock_code = """
// ==========================================
// WAKE LOCK API PARA EVITAR QUE LA TV SE APAGUE
// ==========================================
let wakeLock = null;
const requestWakeLock = async () => {
    try {
        if ('wakeLock' in navigator) {
            wakeLock = await navigator.wakeLock.request('screen');
            console.log('Wake Lock is active! La pantalla no se suspendera.');
        }
    } catch (err) {
        console.error('WakeLock error');
    }
};

document.addEventListener('DOMContentLoaded', requestWakeLock);
document.addEventListener('visibilitychange', () => {
    if (wakeLock !== null && document.visibilityState === 'visible') {
        requestWakeLock();
    }
});
</script>"""

if "requestWakeLock" not in content:
    content = content.replace("</script>", wakelock_code)
    with open('portal/templates/portal/salidas_admin_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
