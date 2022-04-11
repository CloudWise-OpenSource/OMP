import React from "react";
import ReactEcharts from "echarts-for-react";
import echarts from "echarts";

const OmpProgress = ({ trafficWay, percent }) => {
  // 判断trafficWay的每一项是否都是0
  let isAllNull = trafficWay.filter((i) => i.value !== 0);
  //console.log(isAllNull);
  if (isAllNull.length == 0) {
    trafficWay[2].value = 1;
  }

  var data = [];
  var color = [
    "#ee686e",
    "#ffbe40",
    "rgb(84, 187, 166)",
    "#df7153",
    "#fad83a",
    "#c490bf",
    "#1fe15f",
    "#3087d6",
    "#4be1ff",
  ];
  for (var i = 0; i < trafficWay.length; i++) {
    data.push(
      {
        value: trafficWay[i].value,
        name: trafficWay[i].name,
        itemStyle: {
          normal: {
            borderWidth: 4,
            //shadowBlur: 2,
            borderColor: color[i],
            //shadowColor: color[i],
          },
        },
      },
      {
        value: 0,
        name: "",
        itemStyle: {
          normal: {
            label: {
              show: false,
            },
            labelLine: {
              show: false,
            },
            color: percent == 0 ? "#f45966":"rgba(0, 0, 0, 0)",
            borderColor: percent == 0 ? "#f45966":"rgba(0, 0, 0, 0)",
            borderWidth: 4,
          },
        },
      }
    );
  }
  var seriesOption = [
    {
      name: "",
      type: "pie",
      clockWise: false,
      radius: ["75%", "77%"],
      center: ["50%", "50%"],
      hoverAnimation: false,
      itemStyle: {
        normal: {
          label: {
            show: false,
            position: "outside",
            color: "#ddd",
            // formatter: function (params) {
            //   var percent = 0;
            //   var total = 0;
            //   for (var i = 0; i < trafficWay.length; i++) {
            //     total += trafficWay[i].value;
            //   }
            //   percent = ((params.value / total) * 100).toFixed(0);
            //   if (params.name !== "") {
            //     return (
            //       "交通方式：" +
            //       params.name +
            //       "\n" +
            //       "\n" +
            //       "占百分比：" +
            //       percent +
            //       "%"
            //     );
            //   } else {
            //     return "";
            //   }
            // },
          },
          labelLine: {
            length: 30,
            length2: 100,
            show: false,
            color: "#00ffff",
          },
        },
      },
      data: data,
    },
  ];
  const option = {
    // backgroundColor: '#0A2E5D',
    color: color,
    title: {
      text: `${percent == Infinity ? 100 : isNaN(percent) ? 0 : percent}%`,
      top: "37%",
      left: "47%",
      textAlign: "center",
      textStyle: {
        color:
          `${percent == Infinity ? 100 : isNaN(percent) ? 0 : percent}%` ==
          "100%"
            ? "rgb(84, 187, 166)"
            : "rgba(0, 0, 0, 0.65)",
        fontSize: 18,
        fontWeight: "400",
      },
    },
    graphic: {
      elements: [
        {
          type: "image",
          z: 3,
          style: {
            // image: img,
            width: 178,
            height: 178,
          },
          left: "center",
          top: "center",
          position: [100, 100],
        },
      ],
    },
    tooltip: {
      show: false,
    },
    // legend: {
    //   icon: "circle",
    //   orient: "vertical",
    //   // x: 'left',
    //   data: [
    //     "物理机",
    //     "宿主机",
    //     "云主机",
    //     "网络设备",
    //     "安全设备",
    //     "应用系统",
    //     "存储设备",
    //     "网络服务",
    //     "终端PC",
    //   ],
    //   right: "5%",
    //   top: "center",
    //   align: "left",
    //   textStyle: {
    //     color: "black",
    //   },
    //   itemGap: 20,
    //   // formatter: function(name) {
    //   //      let target,percent;
    //   //      for (let i = 0; i < dataPie.length; i++) {
    //   //          if (dataPie[i].name === name) {
    //   //              target = dataPie[i].value;
    //   //              percent = ((target/total)*100).toFixed(2);
    //   //          }
    //   //      }
    //   //      let arr = [ percent+'% '+' {yellow|' + target + '}', ' {blue|' + name + '}' ];
    //   //      return arr.join("\n")

    //   //  }
    // },
    toolbox: {
      show: false,
    },
    series: seriesOption,
  };
  return (
    <ReactEcharts
      option={option}
      notMerge={true}
      lazyUpdate={true}
      //onEvents={onEvents}
      style={{ width: "100px", height: "100px" }}
    />
  );
};

export default OmpProgress;
