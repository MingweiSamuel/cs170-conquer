((teamId) => {
    fetch('https://raw.githubusercontent.com/Berkeley-CS170/project-leaderboard/master/rankings.csv')
        .then(res => res.text()).then(t => t.trim().split('\n').map(s => s.split(',')))
        .then(rows => {
            let [ head, ...data ] = rows;
            data = data.map(r => r.map(n => Number(n)));
            let i = head.indexOf('' + teamId);
            let ranks = data.map(r => [ r[i], r[0] ]).reduce((x, d) => {
                (x[d[0]] = x[d[0]] || []).push(d[1]);
                return x;
            }, {});
            Object.keys(ranks).sort((a, b) => a - b)
                .forEach(n => console.log(`%c${n}/${head.length} (${ranks[n].length}): %c${ranks[n].join(', ')}`, 'font-weight:bold', ''));
        });
})(200);
