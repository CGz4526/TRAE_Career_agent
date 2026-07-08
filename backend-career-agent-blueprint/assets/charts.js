(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var accent3 = style.getPropertyValue('--accent3').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  // --- Chart: 4周开发甘特图 ---
  var chartEl = document.getElementById('chart-gantt');
  if (!chartEl) return;

  var chart = echarts.init(chartEl, null, { renderer: 'svg' });

  // 甘特图数据：使用自定义系列模拟
  var categories = [
    'Phase 4: 优化与演示',
    'Phase 3: 面试+前端集成',
    'Phase 2: 核心Agent开发',
    'Phase 1: 基础框架搭建'
  ];

  var phases = [
    {
      name: '基础框架搭建',
      value: [0, 4, 7, accent],
      itemStyle: { color: accent }
    },
    {
      name: '核心Agent开发',
      value: [1, 7, 14, accent2],
      itemStyle: { color: accent2 }
    },
    {
      name: '面试+前端集成',
      value: [2, 14, 21, accent3],
      itemStyle: { color: accent3 }
    },
    {
      name: '优化与演示准备',
      value: [3, 21, 28, '#f87171'],
      itemStyle: { color: '#f87171' }
    }
  ];

  // 子任务数据
  var subTasks = [
    // Phase 1
    { name: '项目初始化(三端)', value: [0, 0, 2, accent + '99'] },
    { name: '数据库设计+建表', value: [0, 1, 3, accent + '99'] },
    { name: 'JWT认证流程', value: [0, 2, 4, accent + '99'] },
    { name: 'Java→Python通信链路', value: [0, 3, 5, accent + '99'] },
    { name: 'Docker Compose编排', value: [0, 4, 7, accent + '99'] },
    // Phase 2
    { name: 'Prompt模板编写', value: [1, 7, 9, accent2 + '99'] },
    { name: 'Pydantic数据模型', value: [1, 7, 9, accent2 + '99'] },
    { name: '岗位匹配Agent', value: [1, 8, 11, accent2 + '99'] },
    { name: '简历优化Agent', value: [1, 9, 12, accent2 + '99'] },
    { name: '题库生成Agent', value: [1, 10, 13, accent2 + '99'] },
    { name: '项目梳理Agent', value: [1, 11, 14, accent2 + '99'] },
    { name: 'LangGraph编排', value: [1, 12, 14, accent2 + '99'] },
    // Phase 3
    { name: '模拟面试Agent', value: [2, 14, 17, accent3 + '99'] },
    { name: 'WebSocket网关', value: [2, 14, 16, accent3 + '99'] },
    { name: 'Monaco Editor集成', value: [2, 15, 18, accent3 + '99'] },
    { name: '前端页面开发', value: [2, 16, 20, accent3 + '99'] },
    { name: '前后端联调', value: [2, 19, 21, accent3 + '99'] },
    // Phase 4
    { name: 'UI/UX打磨', value: [3, 21, 24, '#f8717199'] },
    { name: '演示数据准备', value: [3, 21, 23, '#f8717199'] },
    { name: '性能优化', value: [3, 23, 26, '#f8717199'] },
    { name: '文档+演示视频', value: [3, 25, 28, '#f8717199'] }
  ];

  var allData = phases.concat(subTasks);

  chart.setOption({
    backgroundColor: 'transparent',
    title: {
      text: '4 周开发周期 · 任务甘特图',
      left: 'center',
      top: 10,
      textStyle: { color: ink, fontSize: 14, fontWeight: 600 }
    },
    tooltip: {
      appendToBody: true,
      formatter: function(params) {
        var d = params.value;
        var start = '第 ' + (d[1] + 1) + ' 天';
        var end = '第 ' + d[2] + ' 天';
        return '<b>' + params.name + '</b><br/>' + start + ' → ' + end + '<br/>耗时: ' + (d[2] - d[1]) + ' 天';
      }
    },
    grid: {
      left: 160,
      right: 40,
      top: 50,
      bottom: 50
    },
    xAxis: {
      type: 'value',
      min: 0,
      max: 28,
      interval: 7,
      axisLabel: {
        color: muted,
        formatter: function(val) {
          return '第' + (Math.floor(val / 7) + 1) + '周';
        }
      },
      axisLine: { lineStyle: { color: rule } },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: ink, fontSize: 12 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    series: [{
      type: 'custom',
      renderItem: function(params, api) {
        var categoryIndex = api.value(0);
        var start = api.coord([api.value(1), categoryIndex]);
        var end = api.coord([api.value(2), categoryIndex]);
        var height = api.size([0, 1])[1] * 0.45;

        var rectShape = {
          type: 'rect',
          transition: ['shape'],
          shape: {
            x: start[0],
            y: start[1] - height / 2,
            width: end[0] - start[0],
            height: height,
            r: 3
          },
          style: {
            fill: api.value(3),
            stroke: api.value(3),
            lineWidth: 0
          }
        };
        return rectShape;
      },
      encode: {
        x: [1, 2],
        y: 0
      },
      data: allData.map(function(item) {
        return {
          name: item.name,
          value: item.value
        };
      }),
      clip: true
    }],
    legend: {
      show: false
    },
    animation: false
  });

  window.addEventListener('resize', function() {
    chart.resize();
  });
})();
