using System;
using UnityEngine;

namespace EZCoach.Value {
    /// <summary>
    /// The class representing a definition of an image. It consists of dimensions of the image (width and height), a number of channels, a range of each pixel's channel and a textual description.
    /// The pixel range is specified by the ChannelRange enumeration.
    /// </summary>
    [Serializable]
    public class PixelList  {
        public readonly string type = "PixelList";
        public int width;
        public int height;
        public int channels;
        public IntRange range;
        public string channel_range;
        public string description;

        public PixelList(int width, int height, int channels, IntRange range, string description = null) {
            this.width = width;
            this.height = height;
            this.channels = channels;
            this.range = range;
            this.description = description;
        }
        
        public PixelList(int width, int height, int channels, ChannelRange channelRange, string description = null) 
            : this(width, height, channels, null, description) {
            this.channel_range = channelRange.ToString().ToLower();
        }
    }

    /// <summary>
    /// Specifies the range of a pixel.
    /// </summary>
    public enum ChannelRange {
        BIT8, NORMALIZED
    }
}