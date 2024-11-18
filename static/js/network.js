// network.js
const width = document.getElementById('network').clientWidth;
const height = 600;

let currentData = null;
let simulation = null;

const svg = d3.select('#network')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

function initializeSimulation() {
    return d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-50))
        .force('center', d3.forceCenter(width / 2, height / 2));
}

function updateNetwork(data, filter = null) {
    currentData = data;

    // Filter nodes and links based on criteria
    let filteredData = filterData(data, filter);

    // Clear previous network
    svg.selectAll('*').remove();

    // Create new simulation
    simulation = initializeSimulation();

    // Create links
    const links = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(filteredData.links)
        .enter()
        .append('line')
        .attr('class', 'link')
        .style('stroke', '#999')
        .style('stroke-opacity', 0.6)
        .style('stroke-width', 1);

    // Create nodes
    const nodes = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('circle')
        .data(filteredData.nodes)
        .enter()
        .append('circle')
        .attr('class', 'node')
        .attr('r', d => getNodeSize(d))
        .style('fill', d => getNodeColor(d))
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add labels
    const labels = svg.append('g')
        .attr('class', 'labels')
        .selectAll('text')
        .data(filteredData.nodes)
        .enter()
        .append('text')
        .text(d => d.id)
        .style('fill', 'white')
        .style('font-size', '8px')
        .attr('dx', 12)
        .attr('dy', 4);

    // Add tooltips
    nodes.append('title')
        .text(d => `${d.id}\nType: ${d.type}\nGoals: ${d.goals}\nAssists: ${d.assists}\nTackles: ${d.tackles}`);

    // Update simulation
    simulation
        .nodes(filteredData.nodes)
        .on('tick', () => {
            links
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            nodes
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            labels
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });

    simulation.force('link')
        .links(filteredData.links);
}

function filterData(data, filter) {
    if (!filter) return data;

    // Filter nodes based on type
    const filteredNodes = data.nodes.filter(node => {
        switch(filter) {
            case 'Scorer':
                return node.goals > 10; // Example threshold
            case 'Defender':
                return node.tackles > 20; // Example threshold
            case 'Assister':
                return node.assists > 8; // Example threshold
            default:
                return true;
        }
    });

    // Get IDs of filtered nodes
    const filteredIds = new Set(filteredNodes.map(node => node.id));

    // Filter links to only include connections between filtered nodes
    const filteredLinks = data.links.filter(link =>
        filteredIds.has(link.source.id || link.source) &&
        filteredIds.has(link.target.id || link.target)
    );

    return {
        nodes: filteredNodes,
        links: filteredLinks
    };
}

function getNodeSize(d) {
    switch(d.type) {
        case 'Scorer': return 8 + d.goals * 0.5;
        case 'Assister': return 8 + d.assists * 0.5;
        case 'Defender': return 8 + d.tackles * 0.2;
        default: return 8;
    }
}

function getNodeColor(d) {
    switch(d.type) {
        case 'Scorer': return '#ff1493';
        case 'Assister': return '#9c27b0';
        case 'Defender': return '#4caf50';
        default: return '#999';
    }
}

// Drag functions
function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
}

function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
}

function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
}

// Event handlers for filters
document.getElementById('topScorers').addEventListener('click', () => {
    updateNetwork(currentData, 'Scorer');
});

document.getElementById('topDefenders').addEventListener('click', () => {
    updateNetwork(currentData, 'Defender');
});

document.getElementById('topAssisters').addEventListener('click', () => {
    updateNetwork(currentData, 'Assister');
});

// Search filter
const searchInput = document.getElementById('searchFilter');
searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    if (searchTerm === '') {
        updateNetwork(currentData);
    } else {
        const filteredData = {
            nodes: currentData.nodes.filter(node =>
                node.id.toLowerCase().includes(searchTerm)
            ),
            links: currentData.links
        };
        updateNetwork(filteredData);
    }
});

// Clear filters
document.querySelector('.filters').addEventListener('click', (e) => {
    if (e.target.classList.contains('clear-filter')) {
        updateNetwork(currentData);
    }
});