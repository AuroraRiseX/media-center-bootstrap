package local.nuvio.catalog;
import android.accessibilityservice.AccessibilityService;import android.view.accessibility.AccessibilityEvent;import android.content.Intent;import android.util.Log;
public class CatalogGuard extends AccessibilityService {
 void ensure(){try{startForegroundService(new Intent(this,CatalogService.class));Log.i("TVCatalog","Local startup guard ensured service");}catch(Exception e){Log.w("TVCatalog","Startup guard waiting for next Nuvio event",e);}}
 protected void onServiceConnected(){ensure();}public void onAccessibilityEvent(AccessibilityEvent e){if(e!=null&&"com.nuvio.tv".contentEquals(e.getPackageName()))ensure();}public void onInterrupt(){}
}
