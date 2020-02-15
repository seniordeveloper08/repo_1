from typing import Optional
from io import BytesIO
from gi.repository import Gst
from utils import must_link
import datetime;

first = 0
flag = 0
index = 0
ct = datetime.datetime.now()
def new_buffer(sink, data):
    global first
    global flag
    global ct
    global index

    sample = sink.emit("pull-sample")
    buf = sample.get_buffer()
    buffer = buf.extract_dup(0, buf.get_size())

    if first == 0:
        first = buf.pts 
        ct = datetime.datetime.now()
        flag = 1
    
    if(flag == 0):
        ct = datetime.datetime.now()
        index +=1
        flag = 1
    if((buf.pts - first) > 2000000000):
        print("./videos/output{}.jpeg".format(index), "-", ct, buf.pts)
        binary_file = open("./videos/output{}.jpeg".format(index), "ab")
        binary_file.write(buffer)
        binary_file.close()
        flag = 0
        first = buf.pts
    

    return Gst.FlowReturn.OK

class JpegSink:
    def __new__(
        cls,
        location: str,
        playlist_location: str,
    ) -> Gst.Element:

        print('sink')

        sink = Gst.ElementFactory.make("appsink")
        sink.set_property("emit-signals", True)
        sink.connect("new-sample", new_buffer, sink)
      
        bin = Gst.Bin()
        bin.add(sink)

        enc = Gst.ElementFactory.make("jpegenc", "encoder")
        bin.add(enc)
        # try:
        try:
            must_link(enc.link(sink))
            #must_link(mpegtsmux.link(sink))
        except RuntimeError as err:
            raise RuntimeError('Could not link source') from err

        sink_pad = enc.get_static_pad('sink')

        ghost_sink = Gst.GhostPad.new('sink', sink_pad)
        bin.add_pad(ghost_sink)
        return bin