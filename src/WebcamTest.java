import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.util.Date;

import javax.imageio.ImageIO;

import me.prettyprint.cassandra.serializers.BytesArraySerializer;
import me.prettyprint.cassandra.serializers.LongSerializer;
import me.prettyprint.cassandra.serializers.StringSerializer;
import me.prettyprint.cassandra.serializers.TimeUUIDSerializer;
import me.prettyprint.hector.api.Cluster;
import me.prettyprint.hector.api.Keyspace;
import me.prettyprint.hector.api.ddl.ColumnFamilyDefinition;
import me.prettyprint.hector.api.ddl.ComparatorType;
import me.prettyprint.hector.api.factory.HFactory;
import me.prettyprint.hector.api.mutation.Mutator;

import com.googlecode.javacv.*;
import static com.googlecode.javacv.cpp.opencv_core.*;

public class WebcamTest {
	public static void createColumnFamily(Cluster cluster) {
		ColumnFamilyDefinition colFamily = HFactory.createColumnFamilyDefinition("v1", "WebcamFrames2", ComparatorType.ASCIITYPE);
		colFamily.setKeyValidationClass("org.apache.cassandra.db.marshal.LongType");
		cluster.addColumnFamily(colFamily, true);
	}
	
	public static void main(String[] args) throws Exception {
		Cluster cluster = HFactory.getOrCreateCluster("Test Cluster", "localhost:9160");
		Keyspace keyspace = HFactory.createKeyspace("v1", cluster);
		Mutator<Long> mutator = HFactory.createMutator(keyspace, LongSerializer.get());
		
		//createColumnFamily(cluster);
		
        CanvasFrame frame = new CanvasFrame("Some Title");

        FrameGrabber grabber = new OpenCVFrameGrabber(0);
        grabber.setImageWidth(640);
        grabber.setImageWidth(480);
        grabber.setBitsPerPixel(16);
        grabber.start();

        int numFrames = 0;
        IplImage grabbedImage = grabber.grab();   
        while (frame.isVisible() && (grabbedImage = grabber.grab()) != null) {
        	grabbedImage = grabber.grab();
            frame.showImage(grabbedImage);            
            BufferedImage bufferedImage = grabbedImage.getBufferedImage();
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ImageIO.write(bufferedImage, "jpg", baos);
            byte[] rawImg = baos.toByteArray();
            long timestamp = new Date().getTime(); 
    		mutator.insert(timestamp, "WebcamFrames2", HFactory.createColumn("Frame", rawImg, StringSerializer.get(), BytesArraySerializer.get()));
    		mutator.insert(timestamp, "WebcamFrames2", HFactory.createColumn("FrameNumber", (long) numFrames, StringSerializer.get(), LongSerializer.get()));
    		numFrames = numFrames + 1;
    		System.out.println("Timestamp: " + timestamp);
        }
        
        grabber.stop();
        frame.dispose();
        System.out.println("Frames saved to db: " + numFrames);
    }
}
