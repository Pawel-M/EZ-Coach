using System;
using UnityEngine;

namespace EZCoach.Value {
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

    public enum ChannelRange {
        BIT8, NORMALIZED
    }
}