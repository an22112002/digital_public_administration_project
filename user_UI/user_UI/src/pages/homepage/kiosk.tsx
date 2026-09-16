import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCategories, getServicesList } from '../../api/servicesAPI';
import type { Service } from '../../api/servicesAPI';
import Header from '../../header/header';
import aiBootsImage from '../../assets/ai boots.png';

function SearchIcon({ className = '' }: { className?: string }) {
	return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.7" /><path d="m16 16 4.2 4.2" strokeLinecap="round" /></svg>;
}

export default function KioskHomePage() {
	const navigate = useNavigate();
	const [searchTerm, setSearchTerm] = useState('');
	const [selectedCategory, setSelectedCategory] = useState('');
	const [categories, setCategories] = useState<string[]>([]);
	const [services, setServices] = useState<Service[]>([]);

	useEffect(() => {
		let active = true;
		getCategories().then((result) => {
			if (active) setCategories(result);
		}).catch(() => {
			if (active) setCategories([]);
		});
		return () => { active = false; };
	}, []);

	useEffect(() => {
		let active = true;
		getServicesList(selectedCategory, searchTerm).then((result) => {
			if (active) setServices(result);
		}).catch(() => {
			if (active) setServices([]);
		});
		return () => { active = false; };
	}, [selectedCategory, searchTerm]);

	const visibleServices = services.slice(0, 5);
	const categoryOptions = categories.length > 0 ? categories : ['Hộ Tịch', 'Chứng Thực', 'Đánh số'];

	return (
		<div className="Kiosk-screen">
			<Header />

			<main className="Kiosk-content">
				<section className="Kiosk-ai-image">
					<h2>DỊCH VỤ CÔNG TRỰC TUYẾN</h2>
					<img src={aiBootsImage} alt="Trợ lý AI hỗ trợ dịch vụ công" />
				</section>

				<label className="Kiosk-search-box" htmlFor="Kiosk-search"><SearchIcon /><input id="Kiosk-search" value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Tìm kiếm dịch vụ..." /></label>
				<div className="Kiosk-category-filter" role="group" aria-label="Lọc dịch vụ">
					<button className={selectedCategory === '' ? 'active' : ''} onClick={() => setSelectedCategory('')}>Tất Cả Dịch Vụ</button>
					{categoryOptions.map((category) => <button key={category} className={selectedCategory === category ? 'active' : ''} onClick={() => setSelectedCategory(category)}>{category.toUpperCase()}</button>)}
				</div>
				<h2 className="Kiosk-list-title">DANH SÁCH DỊCH VỤ HỖ TRỢ NỘP HỒ SƠ TỰ ĐỘNG</h2>
				<section className="Kiosk-service-list">
					{visibleServices.map((service, index) => <button key={service.serviceID} onClick={() => navigate(`/kiosk/scan/${service.serviceID}`)}><span className="Kiosk-service-copy"><span className="Kiosk-service-category">{service.category.toUpperCase()}</span><span className="Kiosk-service-name"><span className="Kiosk-service-number">{index + 1}</span>{service.title}</span></span><span className="Kiosk-chevron">›</span></button>)}
				</section>
			</main>

			<style>{`
				.Kiosk-screen{min-height:100vh;background:#f8fafc;color:#111827;font-family:Arial,sans-serif}.Kiosk-header{height:164px;box-sizing:border-box;padding:25px 4.1%;display:flex;align-items:center;gap:26px;color:#fff;background:#ee7036;box-shadow:0 3px 7px #0002}.Kiosk-brand-mark{width:86px;height:86px;border-radius:50%;display:grid;place-items:center;flex:none;background:#f18a5d;font-size:58px}.Kiosk-header h1{margin:0;font-size:32px;line-height:1.35}.Kiosk-header p{margin:7px 0 0;font-size:24px}.Kiosk-content{padding:26px 3.7% 112px}.Kiosk-guide{min-height:370px;padding:28px 34px;box-sizing:border-box;display:grid;grid-template-columns:330px 1fr;gap:28px;align-items:center;background:#fff;border-radius:23px;box-shadow:0 2px 7px #17203312}.Kiosk-guide>img{width:100%;height:318px;object-fit:cover;border-radius:16px}.Kiosk-section-title{display:flex;align-items:center;gap:16px;color:#475569}.Kiosk-section-title span{height:2px;flex:1;background:#cbd5e1}.Kiosk-section-title h2{margin:0;white-space:nowrap;font-size:23px;letter-spacing:1px}.Kiosk-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin:20px 0 17px;text-align:center}.Kiosk-step-icon{width:48px;height:48px;margin:0 auto 8px;display:grid;place-items:center;border:2px solid #ff6262;border-radius:50%;color:#ff4f54;font-size:27px}.Kiosk-step-icon svg{width:25px;height:25px}.Kiosk-steps b{display:block;font-size:16px;line-height:1.2}.Kiosk-steps p{margin:11px 0 0;color:#7c8492;font-size:14px;line-height:1.35}.Kiosk-notice{display:flex;gap:14px;padding:15px 18px;border:2px solid #ffdc69;border-radius:16px;background:#fffbf0;color:#7c2d12}.Kiosk-bell{color:#f59e0b;font-size:24px;line-height:1}.Kiosk-notice b{font-size:16px}.Kiosk-notice p{margin:3px 0 0;color:#606b7b;font-size:15px;line-height:1.4}.Kiosk-actions{display:grid;grid-template-columns:repeat(3,1fr);gap:25px;margin:27px 0}.Kiosk-action{min-height:260px;padding:19px;box-sizing:border-box;position:relative;border:0;border-radius:22px;color:#fff;text-align:left;cursor:pointer;box-shadow:0 3px 6px #0002}.Kiosk-action.green{background:#4caf50}.Kiosk-action.blue{background:#2189df}.Kiosk-action.gold{background:#eead16}.Kiosk-action>svg,.Kiosk-services-icon{width:65px;height:65px;padding:15px;box-sizing:border-box;display:block;border-radius:16px;background:#ffffff30;font-size:38px;color:#fff}.Kiosk-action strong{display:block;margin-top:15px;font-size:25px;line-height:1.06}.Kiosk-action>span:not(.Kiosk-services-icon){display:block;margin-top:11px;font-size:18px;line-height:1.35}.Kiosk-action i{position:absolute;bottom:17px;left:19px;width:44px;height:44px;border-radius:50%;display:grid;place-items:center;background:#ffffff35}.Kiosk-action i svg{width:25px}.Kiosk-search-box{height:68px;box-sizing:border-box;display:flex;align-items:center;gap:17px;padding:0 25px;background:#fff;border:2px solid #e2e6eb;border-radius:38px}.Kiosk-search-box svg{width:30px;color:#9ba5b4}.Kiosk-search-box input{width:100%;border:0;outline:0;color:#334155;font-size:22px}.Kiosk-search-box input::placeholder{color:#9ba5b4}.Kiosk-list-title{margin:27px 0 20px;color:#c94b20;text-align:center;font-size:22px}.Kiosk-service-list{display:grid;gap:18px}.Kiosk-service-list button{min-height:109px;padding:17px 23px;display:grid;grid-template-columns:60px 1fr auto 24px;grid-template-rows:1fr 1fr;column-gap:17px;align-items:center;text-align:left;background:#fff;border:2px solid #e3e6eb;border-radius:22px;cursor:pointer}.Kiosk-file-badge{width:56px;height:56px;grid-row:1/span 2;display:grid;place-items:center;color:#ff3343;background:#fff4f3;border:2px solid #ffbdc0;border-radius:15px}.Kiosk-file-badge svg{width:30px}.Kiosk-service-name{align-self:end;font-size:21px;font-weight:700}.Kiosk-waiting{align-self:start;color:#7b8492;font-size:18px}.Kiosk-waiting b{color:#ed2e35}.Kiosk-chevron{grid-column:4;grid-row:1/span 2;color:#99a3b2;font-size:43px;font-weight:300}.Kiosk-footer{height:74px;padding:0 4%;box-sizing:border-box;position:fixed;bottom:0;left:0;right:0;display:flex;align-items:center;justify-content:space-between;background:#fff;border-top:2px solid #e5e7eb;color:#e7672d;font-size:22px}.Kiosk-footer span{color:#9ca5b5;font-size:16px}@media(max-width:900px){.Kiosk-header{height:120px}.Kiosk-header h1{font-size:23px}.Kiosk-header p{font-size:17px}.Kiosk-brand-mark{width:64px;height:64px;font-size:40px}.Kiosk-guide{grid-template-columns:220px 1fr;padding:20px}.Kiosk-guide>img{height:250px}.Kiosk-section-title h2{font-size:16px}.Kiosk-steps b{font-size:12px}.Kiosk-steps p,.Kiosk-notice p{font-size:11px}.Kiosk-action{min-height:210px}.Kiosk-action strong{font-size:18px}.Kiosk-action>span:not(.Kiosk-services-icon){font-size:14px}.Kiosk-service-name{font-size:17px}}
			`}</style>
							<style>{`
								@media (min-width: 1400px) {
									.Kiosk-screen { min-height: 1080px; height: 100vh; overflow: hidden; }
									.Kiosk-header { height: 112px; padding: 16px 42px; gap: 20px; }
									.Kiosk-brand-mark { width: 68px; height: 68px; font-size: 44px; }
									.Kiosk-header h1 { font-size: 25px; line-height: 1.15; }
									.Kiosk-header p { margin-top: 4px; font-size: 17px; }
									.Kiosk-content { padding: 16px 42px 70px; }
									.Kiosk-guide { height: 248px; min-height: 0; padding: 18px 24px; grid-template-columns: 235px 1fr; gap: 24px; border-radius: 18px; }
									.Kiosk-guide > img { height: 210px; border-radius: 12px; }
									.Kiosk-section-title { gap: 12px; }
									.Kiosk-section-title h2 { font-size: 18px; }
									.Kiosk-steps { gap: 12px; margin: 12px 0 10px; }
									.Kiosk-step-icon { width: 36px; height: 36px; margin-bottom: 5px; font-size: 20px; }
									.Kiosk-step-icon svg { width: 19px; height: 19px; }
									.Kiosk-steps b { font-size: 12px; }
									.Kiosk-steps p { margin-top: 5px; font-size: 11px; }
									.Kiosk-notice { gap: 10px; padding: 9px 13px; border-radius: 11px; }
									.Kiosk-bell { font-size: 18px; }
									.Kiosk-notice b { font-size: 12px; }
									.Kiosk-notice p { margin-top: 2px; font-size: 11px; line-height: 1.25; }
									.Kiosk-actions { gap: 18px; margin: 16px 0; }
									.Kiosk-action { min-height: 150px; padding: 14px; border-radius: 16px; }
									.Kiosk-action > svg, .Kiosk-services-icon { width: 42px; height: 42px; padding: 10px; border-radius: 11px; font-size: 24px; }
									.Kiosk-action strong { margin-top: 8px; font-size: 19px; }
									.Kiosk-action > span:not(.Kiosk-services-icon) { margin-top: 5px; font-size: 13px; line-height: 1.2; }
									.Kiosk-action i { bottom: 12px; left: 14px; width: 30px; height: 30px; }
									.Kiosk-action i svg { width: 18px; }
									.Kiosk-search-box { height: 48px; gap: 12px; padding: 0 18px; border-radius: 26px; }
									.Kiosk-search-box svg { width: 22px; }
									.Kiosk-search-box input { font-size: 16px; }
									.Kiosk-list-title { margin: 12px 0 10px; font-size: 16px; }
									.Kiosk-service-list { gap: 9px; }
									.Kiosk-service-list button { min-height: 60px; padding: 8px 16px; grid-template-columns: 38px 1fr auto 16px; column-gap: 12px; border-radius: 12px; }
									.Kiosk-file-badge { width: 36px; height: 36px; border-radius: 9px; }
									.Kiosk-file-badge svg { width: 20px; }
									.Kiosk-service-name { font-size: 15px; }
									.Kiosk-waiting { font-size: 13px; }
									.Kiosk-chevron { font-size: 28px; }
									.Kiosk-footer { height: 54px; padding: 0 42px; font-size: 16px; }
									.Kiosk-footer span { font-size: 13px; }
								}
							`}</style>
							<style>{`
								.Kiosk-content { padding-top: 0; }
								.Kiosk-ai-image { display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 8px; margin: 0 0 18px; }
								.Kiosk-ai-image h2 { margin: 0; color: #c94b20; font-size: 30px; font-weight: 900; letter-spacing: .06em; text-align: center; }
								.Kiosk-ai-image img { display: block; width: min(100%, 900px); height: 300px; object-fit: contain; object-position: center; }
								.Kiosk-service-list button { grid-template-columns: 60px 1fr 24px; grid-template-rows: 1fr; }
								.Kiosk-service-name { grid-column: 2; grid-row: 1; align-self: center; }
								.Kiosk-file-badge { grid-row: 1; }
								.Kiosk-chevron { grid-column: 3; grid-row: 1; }
								.Kiosk-footer { display: none; }
							`}</style>
							<style>{`
								.Kiosk-category-filter { display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin: 12px 0 4px; }
								.Kiosk-category-filter button { min-width: 150px; padding: 9px 18px; border: 1px solid #efc5b5; border-radius: 999px; background: #fff; color: #a94b2d; font-size: 15px; font-weight: 700; cursor: pointer; }
								.Kiosk-category-filter button.active, .Kiosk-category-filter button:hover { border-color: #c84d27; background: #c84d27; color: #fff; }
								.Kiosk-service-list button { grid-template-columns: 28px 50px 1fr 22px; }
								.Kiosk-service-number { color: #b85a3d; font-size: 17px; font-weight: 800; text-align: center; }
								.Kiosk-file-badge { grid-column: 2; }
								.Kiosk-service-name { grid-column: 3; }
								.Kiosk-chevron { grid-column: 4; }
								@media (min-width: 1400px) {
									.Kiosk-category-filter { gap: 7px; margin: 7px 0 3px; }
									.Kiosk-category-filter button { min-width: 125px; padding: 6px 13px; font-size: 13px; }
									.Kiosk-service-list button { grid-template-columns: 22px 38px 1fr 18px; gap: 10px; }
									.Kiosk-service-number { font-size: 14px; }
									.Kiosk-file-badge { grid-column: 2; }
									.Kiosk-service-name { grid-column: 3; }
									.Kiosk-chevron { grid-column: 4; }
								}
							`}</style>
							<style>{`
								@media (min-width: 700px) and (max-width: 1399px), (min-width: 700px) and (max-aspect-ratio: 3/4) {
									.Kiosk-screen { width: 100%; max-width: 1080px; min-height: 1770px; margin: 0 auto; overflow-x: hidden; }
									.Kiosk-header { height: 164px; padding: 25px 4.1%; gap: 26px; }
									.Kiosk-brand-mark { width: 86px; height: 86px; font-size: 58px; }
									.Kiosk-header h1 { font-size: 32px; line-height: 1.35; }
									.Kiosk-header p { margin-top: 7px; font-size: 24px; }
									.Kiosk-content { padding: 26px 3.7% 112px; }
									.Kiosk-guide { height: 370px; min-height: 0; padding: 28px 34px; grid-template-columns: 330px 1fr; gap: 28px; }
									.Kiosk-guide > img { height: 318px; }
									.Kiosk-section-title h2 { font-size: 23px; }
									.Kiosk-steps { gap: 15px; margin: 20px 0 17px; }
									.Kiosk-step-icon { width: 48px; height: 48px; font-size: 27px; }
									.Kiosk-step-icon svg { width: 25px; height: 25px; }
									.Kiosk-steps b { font-size: 16px; }
									.Kiosk-steps p { margin-top: 11px; font-size: 14px; }
									.Kiosk-notice { gap: 14px; padding: 15px 18px; border-radius: 16px; }
									.Kiosk-notice b { font-size: 16px; }
									.Kiosk-notice p { font-size: 15px; line-height: 1.4; }
									.Kiosk-actions { gap: 25px; margin: 27px 0; }
									.Kiosk-action { min-height: 260px; padding: 19px; border-radius: 22px; }
									.Kiosk-action > svg, .Kiosk-services-icon { width: 65px; height: 65px; padding: 15px; }
									.Kiosk-action strong { margin-top: 15px; font-size: 25px; }
									.Kiosk-action > span:not(.Kiosk-services-icon) { margin-top: 11px; font-size: 18px; line-height: 1.35; }
									.Kiosk-search-box { height: 68px; padding: 0 25px; }
									.Kiosk-search-box input { font-size: 22px; }
									.Kiosk-list-title { margin: 27px 0 20px; font-size: 22px; }
									.Kiosk-service-list { gap: 18px; }
									.Kiosk-service-list button { min-height: 109px; padding: 17px 23px; grid-template-columns: 60px 1fr auto 24px; column-gap: 17px; border-radius: 22px; }
									.Kiosk-file-badge { width: 56px; height: 56px; border-radius: 15px; }
									.Kiosk-file-badge svg { width: 30px; }
									.Kiosk-service-name { font-size: 21px; }
									.Kiosk-waiting { font-size: 18px; }
									.Kiosk-chevron { font-size: 43px; }
									.Kiosk-footer { height: 74px; padding: 0 4%; font-size: 22px; }
									.Kiosk-footer span { font-size: 16px; }
								}
							`}</style>
							<style>{`
								.Kiosk-service-list button { grid-template-columns: 60px 1fr 24px; grid-template-rows: 1fr; }
								.Kiosk-service-name { grid-column: 2; grid-row: 1; align-self: center; }
								.Kiosk-file-badge { grid-row: 1; }
								.Kiosk-chevron { grid-column: 3; grid-row: 1; }
								.Kiosk-footer { display: none; }
							`}</style>
							<style>{`
								.Kiosk-screen { background: #fff8f3; color: #263238; font-family: 'Inter', 'Segoe UI', sans-serif; }
								.Kiosk-content { padding: 18px 4.5% 32px; }
								.Kiosk-ai-image { margin-bottom: 22px; padding: 20px 28px 14px; background: #fff; border: 1px solid #f4d4c5; border-radius: 24px; box-shadow: 0 8px 22px rgba(146, 57, 25, .08); }
								.Kiosk-ai-image h2 { color: #b83f1d; font-size: clamp(24px, 2.1vw, 34px); letter-spacing: .04em; line-height: 1.15; }
								.Kiosk-ai-image img { width: min(100%, 880px); height: 260px; }
								.Kiosk-search-box { height: 62px; border-color: #f0d9cf; background: #fff; box-shadow: 0 4px 12px rgba(58, 38, 30, .05); }
								.Kiosk-search-box svg { color: #c56a4a; width: 26px; }
								.Kiosk-search-box input { color: #3f4850; font-size: 19px; }
								.Kiosk-list-title { margin: 20px 0 14px; color: #b83f1d; font-size: clamp(17px, 1.6vw, 23px); font-weight: 800; letter-spacing: .025em; }
								.Kiosk-service-list { gap: 12px; }
								.Kiosk-service-list button { min-height: 86px; padding: 13px 20px; grid-template-columns: 50px 1fr 22px; gap: 15px; border: 1px solid #efdeda; border-radius: 16px; background: #fff; box-shadow: 0 3px 10px rgba(58, 38, 30, .04); transition: border-color .2s, box-shadow .2s, transform .2s; }
								.Kiosk-service-list button:hover { border-color: #ef9d7f; box-shadow: 0 7px 18px rgba(184, 63, 29, .12); transform: translateY(-1px); }
								.Kiosk-file-badge { width: 48px; height: 48px; border-color: #f2b5a4; background: #fff5f1; color: #ee4937; border-radius: 12px; }
								.Kiosk-file-badge svg { width: 25px; }
								.Kiosk-service-name { color: #263238; font-size: 18px; line-height: 1.25; font-weight: 700; }
								.Kiosk-chevron { color: #c56a4a; font-size: 36px; line-height: 1; }
								@media (min-width: 1400px) {
									.Kiosk-content { padding: 14px 42px 28px; }
									.Kiosk-ai-image { margin-bottom: 14px; padding: 10px 20px 6px; border-radius: 18px; }
									.Kiosk-ai-image h2 { font-size: 26px; }
									.Kiosk-ai-image img { height: 210px; }
									.Kiosk-search-box { height: 48px; }
									.Kiosk-list-title { margin: 11px 0 8px; font-size: 17px; }
									.Kiosk-service-list { gap: 8px; }
									.Kiosk-service-list button { min-height: 62px; padding: 8px 15px; grid-template-columns: 38px 1fr 18px; gap: 11px; border-radius: 11px; }
									.Kiosk-file-badge { width: 36px; height: 36px; border-radius: 9px; }
									.Kiosk-file-badge svg { width: 20px; }
									.Kiosk-service-name { font-size: 15px; }
									.Kiosk-chevron { font-size: 28px; }
								}
							`}</style>
							<style>{`
								.Kiosk-service-list button { display: grid; grid-template-columns: minmax(0, 1fr) 24px !important; grid-template-rows: 1fr; align-items: center; column-gap: 14px; }
								.Kiosk-service-copy { grid-column: 1 !important; grid-row: 1 !important; min-width: 0; display: flex; flex-direction: column; gap: 6px; }
								.Kiosk-service-copy { align-items: flex-start; text-align: left; }
								.Kiosk-service-category { min-height: 16px; color: #a24a0a; font-size: 14px; font-weight: 800; letter-spacing: .04em; line-height: 1.1; text-align: left; }
								.Kiosk-service-number { display: inline-flex; min-width: 28px; height: 28px; margin-right: 9px; align-items: center; justify-content: center; border-radius: 999px; background: #a24a0a; color: #fff; font-size: 12px; font-weight: 900; vertical-align: middle; }
								.Kiosk-service-name { display: flex; min-height: 28px; align-items: center; grid-column: auto !important; grid-row: auto !important; min-width: 0; overflow-wrap: anywhere; text-align: left; }
								.Kiosk-chevron { grid-column: 2 !important; grid-row: 1 !important; }
								@media (min-width: 1400px) {
									.Kiosk-service-list button { grid-template-columns: minmax(0, 1fr) 18px !important; column-gap: 10px; }
									.Kiosk-service-copy { gap: 3px; }
									.Kiosk-service-category { min-height: 12px; font-size: 11px; }
									.Kiosk-service-number { min-width: 22px; height: 22px; margin-right: 7px; font-size: 10px; }
									.Kiosk-service-name { min-height: 22px; }
								}
							`}</style>
							<style>{`
								.Kiosk-ai-image h2 { font-size: clamp(32px, 3vw, 48px); }
								.Kiosk-search-box { height: 78px; }
								.Kiosk-search-box svg { width: 34px; }
								.Kiosk-search-box input { font-size: 26px; }
								.Kiosk-category-filter { gap: 14px; margin: 18px 0 8px; }
								.Kiosk-category-filter button { min-width: 190px; padding: 13px 24px; font-size: 20px; }
								.Kiosk-list-title { margin: 26px 0 18px; font-size: clamp(22px, 2vw, 32px); }
								.Kiosk-service-list { gap: 16px; }
								.Kiosk-service-list button { min-height: 112px; padding: 18px 24px; border-radius: 18px; }
								.Kiosk-service-copy { gap: 9px; }
								.Kiosk-service-category { min-height: 22px; font-size: 19px; }
								.Kiosk-service-number { min-width: 38px; height: 38px; margin-right: 12px; font-size: 17px; }
								.Kiosk-service-name { min-height: 38px; font-size: 25px; line-height: 1.25; }
								.Kiosk-chevron { font-size: 46px; }
								@media (min-width: 1400px) {
									.Kiosk-ai-image { padding: 12px 24px 8px; }
									.Kiosk-ai-image h2 { font-size: 34px; }
									.Kiosk-ai-image img { height: 250px; }
									.Kiosk-search-box { height: 62px; }
									.Kiosk-search-box svg { width: 28px; }
									.Kiosk-search-box input { font-size: 21px; }
									.Kiosk-category-filter { gap: 10px; margin: 10px 0 5px; }
									.Kiosk-category-filter button { min-width: 150px; padding: 9px 18px; font-size: 16px; }
									.Kiosk-list-title { margin: 14px 0 10px; font-size: 21px; }
									.Kiosk-service-list { gap: 10px; }
									.Kiosk-service-list button { min-height: 78px; padding: 11px 18px; border-radius: 13px; }
									.Kiosk-service-copy { gap: 5px; }
									.Kiosk-service-category { min-height: 16px; font-size: 14px; }
									.Kiosk-service-number { min-width: 28px; height: 28px; margin-right: 9px; font-size: 13px; }
									.Kiosk-service-name { min-height: 28px; font-size: 18px; }
									.Kiosk-chevron { font-size: 34px; }
								}
							`}</style>
							<style>{`
								.Kiosk-ai-image { min-height: 390px; padding: 30px 34px 24px; background: linear-gradient(135deg, #6b351f 0%, #934c28 52%, #c46b3d 100%); border-color: #d79568; box-shadow: 0 10px 26px rgba(101, 48, 27, .2); }
								.Kiosk-ai-image h2 { color: #fff3df; font-size: clamp(32px, 3vw, 48px); text-shadow: 0 2px 5px rgba(55, 25, 14, .35); }
								.Kiosk-ai-image img { width: min(100%, 980px); height: 315px; }
								@media (min-width: 1400px) {
									.Kiosk-ai-image { min-height: 315px; padding: 18px 28px 12px; }
									.Kiosk-ai-image h2 { font-size: 34px; }
									.Kiosk-ai-image img { height: 245px; }
								}
							`}</style>
							<style>{`
								.Kiosk-service-list button { text-align: left !important; }
								.Kiosk-service-copy { width: 100%; align-items: flex-start !important; justify-self: start; text-align: left !important; }
								.Kiosk-service-category, .Kiosk-service-name { width: 100%; text-align: left !important; justify-content: flex-start; }
								.Kiosk-service-number { flex: 0 0 auto; }
							`}</style>
		</div>
	);
}

