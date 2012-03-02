import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;

import javax.imageio.ImageIO;

import me.prettyprint.cassandra.model.CqlQuery;
import me.prettyprint.cassandra.model.CqlRows;
import me.prettyprint.cassandra.serializers.BytesArraySerializer;
import me.prettyprint.cassandra.serializers.LongSerializer;
import me.prettyprint.cassandra.serializers.StringSerializer;
import me.prettyprint.hector.api.Cluster;
import me.prettyprint.hector.api.Keyspace;
import me.prettyprint.hector.api.beans.Row;
import me.prettyprint.hector.api.factory.HFactory;
import me.prettyprint.hector.api.query.QueryResult;

import com.googlecode.javacv.CanvasFrame;
import com.googlecode.javacv.cpp.opencv_core.IplImage;


public class WebcamTestFromDb {
	private static BufferedImage imgFromByteBuffer(byte[] buf) {
		try {
			InputStream in = new ByteArrayInputStream(buf);
            return(ImageIO.read(in));
		} catch(IOException ex) {
			ex.printStackTrace();
			return null;
		}
	}
	
	public static void main(String[] args) {
		Cluster cluster = HFactory.getOrCreateCluster("Test Cluster", "localhost:9160");
		Keyspace keyspace = HFactory.createKeyspace("v1", cluster);
        CanvasFrame frame = new CanvasFrame("Some Title");
        
        CqlQuery<Long, String, byte[]> cqlQuery = new CqlQuery<Long, String, byte[]>(keyspace, LongSerializer.get(), StringSerializer.get(), BytesArraySerializer.get());
        cqlQuery.setQuery("select * from WebcamFrames");
        QueryResult<CqlRows<Long, String, byte[]>> result = cqlQuery.execute();
        
        if (result == null || result.get() == null)
        	return;
        
        int numFrames = 0;
        List<Row<Long, String, byte[]>> list = result.get().getList();
        for (Row<Long, String, byte[]> row: list) {
        	System.out.println("Showing image");
        	//byte[] webcamFrame = row.getColumnSlice().getColumnByName("Frame").getValue();
        	byte[] webcamFrame = row.getColumnSlice().getColumns().get(1).getValue();
        	BufferedImage webcamImage = imgFromByteBuffer(webcamFrame);
        	IplImage image = IplImage.createFrom(webcamImage);
        	frame.showImage(image);
        	// try{Thread.sleep(30);} catch(Exception ex) {ex.printStackTrace();}
        	numFrames++;
        }
        
        frame.dispose();
        System.out.println("Frames played back from db: " + numFrames);
	}
}
