from typing import Optional
from io import BytesIO
from gi.repository import Gst
from utils import must_link
import datetime;

first = 0
flag = 0
index = 0
ct = datetime.datetime.now()
def new_buffer(sink, data, location):
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
    binary_file = open("../share/{}/videos/output{}.ts".format(location, index), "ab")
    binary_file.write(buffer)
    binary_file.close()
    if((buf.pts - first) > 2000000000):
        print("./videos/output{}.ts".format(index), "-", ct, buf.pts)
        flag = 0
        first = buf.pts
    

    return Gst.FlowReturn.OK

class HLSAPPSINK:
    def __new__(
        cls,
        location: int
    ) -> Gst.Element:

        print('sink')

        sink = Gst.ElementFactory.make("appsink")
        sink.set_property("emit-signals", True)
        sink.connect("new-sample", new_buffer, sink, location)
        # sink.set_property("location", location)
        # sink.set_property("target-duration", 5)
        # sink.set_property("playlist-location", playlist_location)
      
        bin = Gst.Bin()
        bin.add(sink);

        enc = Gst.ElementFactory.make("x264enc")
        enc.set_property("bitrate", 4000)
        enc.set_property("tune", "zerolatency")
        enc.set_property("key-int-max", 60)
        enc.set_property("speed-preset", "ultrafast")
        bin.add(enc)

        mpegtsmux = Gst.ElementFactory.make("mpegtsmux", "mpegtsmux")
        if not mpegtsmux:
            sys.stderr.write(" Unable to create mpegtsmux \n")
        bin.add(mpegtsmux)

        # try:
        try:
            must_link(enc.link(mpegtsmux))
            must_link(mpegtsmux.link(sink))
        except RuntimeError as err:
            raise RuntimeError('Could not link source') from err

        sink_pad = enc.get_static_pad('sink')

        ghost_sink = Gst.GhostPad.new('sink', sink_pad)
        bin.add_pad(ghost_sink)
        return bin

class OSDH264RTMPSink:

    def __new__(
        cls,
        location: str,
        # bitrate = 2000000
    ) -> Gst.Element:
        rtmpsink = Gst.ElementFactory.make("rtmpsink")
        rtmpsink.set_property("location", location)

        bin = Gst.Bin()
        bin.add(rtmpsink)


        enc = Gst.ElementFactory.make("x264enc")
        enc.set_property("bitrate", 4000)
        enc.set_property("tune", "zerolatency")
        enc.set_property("key-int-max", 60)
        enc.set_property("speed-preset", "ultrafast")
        bin.add(enc)

        flvmux = Gst.ElementFactory.make("flvmux")
        
        if not flvmux:
            sys.stderr.write(" Unable to create flvmux \n")
        bin.add(flvmux)

        # flvmux.set_property("streamable", True)
        # flvmux.set_property("latency", 500)
        bin.add(flvmux)
        # print(flvmux)
   
        try:
            must_link(enc.link(flvmux))
            must_link(flvmux.link(rtmpsink))
        except RuntimeError as err:
            raise RuntimeError('Could not link source') from err

        print('osd')
        sink= enc.get_static_pad('sink')
        ghost_pad = Gst.GhostPad.new('sink', sink)
        bin.add_pad(ghost_pad)
        return bin
