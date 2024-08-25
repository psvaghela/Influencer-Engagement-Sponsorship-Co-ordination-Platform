import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'spiderman'

db = SQLAlchemy(app)

############################ Models #############################

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default="influencer")
    remarks = db.Column(db.String, default='active')

    influencer = db.relationship('Influencer', backref='user', uselist=False)
    sponsor = db.relationship('Sponsor', backref='user', uselist=False)

class Influencer(db.Model):
    __tablename__ = 'influencers'
    influencer_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    platforms = db.Column(db.String)
    reach = db.Column(db.String)
    category = db.Column(db.String)
    bio = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    sponsor_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    sponsor_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    industry = db.Column(db.String)
    description = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    campaign_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    campaign_name = db.Column(db.String, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsors.sponsor_id'))
    budget = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    visibility = db.Column(db.String)
    goals = db.Column(db.String)
    remarks = db.Column(db.String, default='active')

    sponsor = db.relationship('Sponsor', backref='campaigns')



class Ad(db.Model):
    __tablename__ = 'ad_requests'
    ad_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    ad_name = db.Column(db.String)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.campaign_id'))
    requirements = db.Column(db.String)
    payment_amount = db.Column(db.Integer)
    payment_requested = db.Column(db.Integer)
    status = db.Column(db.String)
    spo_id = db.Column(db.Integer, db.ForeignKey('sponsors.sponsor_id'))
    inf_id = db.Column(db.Integer, db.ForeignKey('influencers.influencer_id'))

    campaign = db.relationship('Campaign', backref='ads')
    influencer = db.relationship('Influencer', backref='ads')





############################ Routes-Influencer #############################

# Login Page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.user_id
            if user.role == 'influencer':
                return redirect(url_for('inf_prof'))
            elif user.role == 'sponsor':
                return redirect(url_for('spo_prof'))
            elif user.role == 'admin':
                return redirect(url_for('admin_campaigns'))
    return render_template("index.html")

# Influencer Registration
@app.route('/influencer-register', methods=['GET', 'POST'])
def influencer_register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        platforms = request.form.get('platforms')
        reach = request.form.get('reach')
        category = request.form.get('category')
        bio = request.form.get('bio')

        # Create user entry
        new_user = User(username=username, password=password, role='influencer')
        db.session.add(new_user)
        db.session.commit()

        # Create influencer entry
        new_influencer = Influencer(name=username, email=email, platforms=platforms, reach=reach, category=category, bio=bio, user_id=new_user.user_id)
        db.session.add(new_influencer)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('inf-registration.html')

# Influencer Profile
@app.route('/inf-prof', methods=['GET', 'POST'])
def inf_prof():
    if 'user_id' in session:
        inf = Influencer.query.filter_by(user_id=session['user_id']).first()
        if inf:
            return render_template('inf-prof.html', inf=inf)
    return redirect(url_for('index'))

# Influencer edit profile
@app.route('/edit-inf-profile', methods=['GET', 'POST'])
def edit_inf_profile():
    if 'user_id' in session:
        inf = Influencer.query.filter_by(user_id=session['user_id']).first()
        if request.method == 'POST':
            inf.name = request.form['name']
            inf.email = request.form['email']
            inf.platforms = request.form['platforms']
            inf.reach = request.form['reach']
            inf.category = request.form['category']
            inf.bio = request.form['bio']
            db.session.commit()
            return redirect(url_for('inf_prof'))
        return render_template('inf-prof-edit.html', inf=inf)
    return redirect(url_for('index'))

# Influencer Ad requests
@app.route('/inf-requests', methods=['GET', 'POST'])
def inf_requests():
    if 'user_id' in session:
        inf = Influencer.query.filter_by(user_id=session['user_id']).first()
        if inf:
            inf_id = inf.influencer_id
            requests = Ad.query.filter_by(inf_id=inf_id, status='Pending').all()
            ads = Ad.query.filter_by(inf_id=inf_id, status='Accepted').all()
            return render_template('inf-requests.html', requests=requests, active_ads=ads)
    return redirect(url_for('index'))

# Influencer view ad
@app.route('/ad/<int:ad_id>', methods=['GET'])
def view_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    return render_template('inf-ad.html', ad=ad)

# Influencer accept ad request
@app.route('/ad/<int:ad_id>/accept', methods=['POST'])
def accept_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    ad.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('inf_requests'))

# Influencer reject ad request
@app.route('/ad/<int:ad_id>/reject', methods=['POST'])
def reject_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    return redirect(url_for('inf_requests'))

# Influencer negotiate payment amount
@app.route('/ad/<int:ad_id>/request_payment', methods=['POST'])
def request_payment(ad_id):
    if 'user_id' in session:
        ad = Ad.query.get_or_404(ad_id)
        new_requested_amount = request.form.get('requested_amount')
        
        ad.payment_requested = new_requested_amount
        db.session.commit()
        
        return redirect(url_for('inf_requests'))
    return redirect(url_for('index'))

# Influencer search public campaigns
@app.route('/inf-search', methods=['GET', 'POST'])
def inf_search():
    if 'user_id' in session:
        if request.method == 'POST':
            campaign_name = request.form.get('campaign_name')
            if campaign_name:
                campaigns = Campaign.query.filter(Campaign.campaign_name.ilike(f'%{campaign_name}%')).filter_by(visibility='public').all()
        else:
            campaigns = Campaign.query.filter_by(visibility='public').all()
        return render_template('inf-search.html', campaigns=campaigns)
    return redirect(url_for('inf_prof'))

# Influencer view campaign
@app.route('/campaign-details/<int:campaign_id>', methods=['GET', 'POST'])
def campaign_details(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('inf-campaign.html', campaign=campaign)

# Influencer stats
@app.route('/inf-stats', methods=['GET'])
def inf_stats():
    if 'user_id' in session:
        inf = Influencer.query.filter_by(user_id=session['user_id']).first()
        if inf:
            # Calculate stats
            total_ads_done = Ad.query.filter_by(inf_id=inf.influencer_id, status='Accepted').count()
            total_pending_requests = Ad.query.filter_by(inf_id=inf.influencer_id, status='Pending').count()
            total_earnings = db.session.query(db.func.sum(Ad.payment_amount)).filter_by(inf_id=inf.influencer_id, status='Accepted').scalar() or 0
            average_earning_per_ad = total_earnings / total_ads_done if total_ads_done > 0 else 0

            stats = {
                'total_ads_done': total_ads_done,
                'total_pending_requests': total_pending_requests,
                'total_earnings': total_earnings,
                'average_earning_per_ad': average_earning_per_ad,
            }

            return render_template('inf-stats.html', inf=inf, stats=stats)
    return redirect(url_for('index'))





############################ Routes-Sponsor #############################

# Sponsor Registration
@app.route('/sponsor-register', methods=['GET', 'POST'])
def sponsor_register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        industry = request.form.get('industry')
        description = request.form.get('description')

        # Create user entry
        new_user = User(username=username, password=password, role='sponsor')
        db.session.add(new_user)
        db.session.commit()

        # Create sponsor entry
        new_sponsor = Sponsor(sponsor_name=username, email=email, industry=industry, description=description, user_id=new_user.user_id)
        db.session.add(new_sponsor)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('spo-registration.html')

# Sponsor Profile
@app.route('/spo-prof', methods=['GET', 'POST'])
def spo_prof():
    if 'user_id' in session:
        spo = Sponsor.query.filter_by(user_id=session['user_id']).first()
        if spo:
            return render_template('spo-prof.html', spo=spo)
    return redirect(url_for('index'))

# Sponsor edit profile
@app.route('/edit-spo-profile', methods=['GET', 'POST'])
def edit_spo_profile():
    if 'user_id' in session:
        spo = Sponsor.query.filter_by(user_id=session['user_id']).first()
        if request.method == 'POST':
            spo.sponsor_name = request.form['sponsor_name']
            spo.email = request.form['email']
            spo.industry = request.form['industry']
            spo.description = request.form['description']
            db.session.commit()
            return redirect(url_for('spo_prof'))
        return render_template('spo-prof-edit.html', spo=spo)
    return redirect(url_for('index'))

# Sponsor active campaigns
@app.route('/spo-campaigns', methods=['GET', 'POST'])
def spo_campaigns():
    if 'user_id' in session:
        sponsor = Sponsor.query.filter_by(user_id=session['user_id']).first()
        if sponsor:
            sponsor_id = sponsor.sponsor_id
            campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
            return render_template('spo-campaigns.html', campaigns=campaigns)
    return redirect(url_for('index'))

# Sponsor view campaign
@app.route('/campaign/<int:campaign_id>', methods=['GET'])
def view_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign:
        ads = Ad.query.filter_by(campaign_id=campaign_id).all()
        return render_template('spo-campaign-view.html', campaign=campaign, ads=ads)
    return redirect(url_for('spo_campaigns'))

# Sponsor edit campaign
@app.route('/campaign/<int:campaign_id>/edit', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        campaign.campaign_name = request.form['campaign_name']
        campaign.budget = request.form['budget']
        campaign.description = request.form['description']
        campaign.start_date = request.form['start_date']
        campaign.end_date = request.form['end_date']
        campaign.visibility = request.form['visibility']
        campaign.goals = request.form['goals']
        db.session.commit()
        return redirect(url_for('view_campaign', campaign_id=campaign_id))
    return render_template('spo-edit-campaign.html', campaign=campaign)

# Sponsor delete campaign
@app.route('/campaign/<int:campaign_id>/delete', methods=['POST'])
def delete_campaign_spo(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    Ad.query.filter_by(campaign_id=campaign_id).delete()
    db.session.delete(campaign)
    db.session.commit()
    return redirect(url_for('spo_campaigns'))

# Sponsor create new campaign
@app.route('/campaign/new', methods=['GET', 'POST'])
def create_campaign():
    if 'user_id' in session:
        sponsor = Sponsor.query.filter_by(user_id=session['user_id']).first()
        if request.method == 'POST':
            campaign_name = request.form['campaign_name']
            budget = request.form['budget']
            description = request.form['description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            visibility = request.form['visibility']
            goals = request.form['goals']
            new_campaign = Campaign(campaign_name=campaign_name, sponsor_id=sponsor.sponsor_id, budget=budget,
                                    description=description, start_date=start_date, end_date=end_date, 
                                    visibility=visibility, goals=goals)
            db.session.add(new_campaign)
            db.session.commit()
            return redirect(url_for('spo_campaigns'))
        return render_template('spo-create-campaign.html')
    return redirect(url_for('index'))

# Sponsor ad requests
@app.route('/spo-requests', methods=['GET', 'POST'])
def spo_requests():
    if 'user_id' in session:
        spo = Sponsor.query.filter_by(user_id=session['user_id']).first()
        if spo:
            spo_id = spo.sponsor_id
            requests = Ad.query.filter_by(spo_id=spo_id).all()
            return render_template('spo-requests.html', requests=requests)
    return redirect(url_for('index'))

# Sponsor view ad request
@app.route('/ad_spo/<int:ad_id>', methods=['GET'])
def view_ad_spo(ad_id):
    if 'user_id' in session:
        ad = Ad.query.get_or_404(ad_id)
        if ad:
            return render_template('spo-ad.html', ad=ad)
    return redirect(url_for('index'))

# Sponsor edit ad request
@app.route('/ad/<int:ad_id>/edit', methods=['GET', 'POST'])
def edit_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    if request.method == 'POST':
        ad_name = request.form.get('ad_name')
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')

        ad.ad_name = ad_name
        ad.requirements = requirements
        ad.payment_amount = payment_amount

        db.session.commit()
        return redirect(url_for('view_ad_spo', ad_id=ad_id))
    
    return render_template('spo-edit-ad.html', ad=ad)

# Sponsor detete ad request
@app.route('/ad/<int:ad_id>/delete', methods=['POST'])
def delete_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    if ad.status == 'Pending':
        db.session.delete(ad)
        db.session.commit()
    return redirect(url_for('spo_requests'))

# Sponsor approve payment negotation amount
@app.route('/ad/<int:ad_id>/approve_payment', methods=['POST'])
def approve_payment(ad_id):
    if 'user_id' in session:
        ad = Ad.query.get_or_404(ad_id)
        # Approve the new payment amount
        ad.payment_amount = ad.payment_requested
        ad.payment_requested = None  # Clear the requested amount
        db.session.commit()
        return redirect(url_for('spo_requests'))
    return redirect(url_for('index'))

# Sponsor reject payment negotiation amount
@app.route('/ad/<int:ad_id>/reject_payment', methods=['POST'])
def reject_payment(ad_id):
    if 'user_id' in session:
        ad = Ad.query.get_or_404(ad_id)
        # Reject the requested amount
        ad.payment_requested = None  # Clear the requested amount
        db.session.commit()
        return redirect(url_for('spo_requests'))
    return redirect(url_for('index'))

# Sponsor search influencers
@app.route('/spo-search', methods=['GET', 'POST'])
def spo_search():
    if 'user_id' in session:
        if request.method == 'POST':
            influencer_name = request.form.get('influencer_name')
            if influencer_name:
                infs = Influencer.query.filter(Influencer.name.ilike(f'%{influencer_name}%')).all()
        else:
            infs = Influencer.query.all()
        return render_template('spo-search.html', infs=infs)
    return redirect(url_for('index'))

# Sponsor view influencer profile
@app.route('/influencer/<int:influencer_id>', methods=['GET', 'POST'])
def influencer_view(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    sponsor_id = Sponsor.query.filter_by(user_id=session['user_id']).first().sponsor_id
    if request.method == 'POST':
        campaign_id = request.form['campaign_id']
        ad_name = request.form['ad_name']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        sponsor_id = Sponsor.query.filter_by(user_id=session['user_id']).first().sponsor_id

        ad_request = Ad(
            ad_name=ad_name,
            campaign_id=campaign_id,
            requirements=requirements,
            payment_amount=payment_amount,
            status='Pending',
            spo_id=sponsor_id,
            inf_id=influencer_id
        )

        db.session.add(ad_request)
        db.session.commit()
        return redirect(url_for('spo_requests'))
    
    # Fetch active campaigns
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id)
    return render_template('spo-influencer.html', influencer=influencer, campaigns=campaigns)





############################ Routes-Admin #############################

# Admin all campaigns
@app.route('/admin-campaigns', methods=['GET'])
def admin_campaigns():
    if 'user_id' in session:
        active_campaigns = Campaign.query.filter_by(remarks='active').all()
        flagged_campaigns = Campaign.query.filter_by(remarks='flagged').all()
        return render_template('admin-campaigns.html', active_campaigns=active_campaigns, flagged_campaigns=flagged_campaigns)
    return redirect(url_for('index'))

# Admin view campaign
@app.route('/view-campaign/<int:campaign_id>', methods=['GET'])
def view_campaign_admin(campaign_id):
    if 'user_id' in session:
        campaign = Campaign.query.get(campaign_id)
        ads = Ad.query.filter_by(campaign_id=campaign_id).all()
        if campaign:
            return render_template('admin-view-campaign.html', campaign=campaign, ads=ads)
    return redirect(url_for('admin_campaigns'))

# Admin flag campaign
@app.route('/flag-campaign/<int:campaign_id>', methods=['POST'])
def flag_campaign(campaign_id):
    if 'user_id' in session:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            campaign.remarks = 'flagged'
            db.session.commit()
    return redirect(url_for('admin_campaigns'))

# Admin delete campaign
@app.route('/delete-campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    if 'user_id' in session:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            Ad.query.filter_by(campaign_id=campaign_id).delete()
            db.session.delete(campaign)
            db.session.commit()
    return redirect(url_for('admin_campaigns'))

# Admin all users
@app.route('/admin-users', methods=['GET', 'POST'])
def admin_users():
    if 'user_id' in session:
        if request.method == 'POST':
            search_query = request.form.get('search_query')
            users = User.query.filter(
                User.username.ilike(f'%{search_query}%'),
                User.remarks != 'flagged'
            ).all()
        else:
            users = User.query.filter_by(remarks='active').filter(
                User.role.in_(['influencer', 'sponsor'])
            ).all()

        flagged_users = User.query.filter_by(remarks='flagged').all()

        return render_template('admin-users.html', users=users, flagged_users=flagged_users)
    return redirect(url_for('index'))

# Admin view user
@app.route('/view-user/<int:user_id>', methods=['GET'])
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    if user:
        influencer = Influencer.query.filter_by(user_id=user_id).first()
        sponsor = Sponsor.query.filter_by(user_id=user_id).first()
        if influencer:
            return render_template('admin-view-user.html', user=user, influencer=influencer)
        elif sponsor:
            return render_template('admin-view-user.html', user=user, sponsor=sponsor)
    return redirect(url_for('admin_users'))

# Admin flag user
@app.route('/flag-user/<int:user_id>', methods=['POST'])
def flag_user(user_id):
    user = User.query.get_or_404(user_id)
    if user:
        user.remarks = 'flagged'
        db.session.commit()
    return redirect(url_for('admin_users'))

# Admin delete user
@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user:
        if user.role == 'sponsor':
            campaigns = Campaign.query.filter_by(sponsor_id=user.sponsor.sponsor_id).all()
            for campaign in campaigns:
                Ad.query.filter_by(campaign_id=campaign.campaign_id).delete()
            Campaign.query.filter_by(sponsor_id=user.sponsor.sponsor_id).delete()
        elif user.role == 'influencer':
            Ad.query.filter_by(inf_id=user.influencer.influencer_id).delete()
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin_users'))

# Admin stats
@app.route('/admin-stats', methods=['GET'])
def admin_stats():
    if 'user_id' in session:
        total_users = User.query.count()
        total_influencers = User.query.filter_by(role='influencer', remarks='active').count()
        total_sponsors = User.query.filter_by(role='sponsor', remarks='active').count()
        total_campaigns = Campaign.query.count()
        total_active_ads = Ad.query.filter_by(status='Accepted').count()
        total_transaction_amount = db.session.query(db.func.sum(Ad.payment_amount)).scalar() or 0
        
        # Generate pie chart
        labels = ['Influencers', 'Sponsors']
        sizes = [total_influencers, total_sponsors]
        colors = ['#ff9999','#66b3ff']
        explode = (0.1, 0)  # explode 1st slice
        
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        # Save the pie chart to the static folder
        static_folder = os.path.join(current_dir, 'static')
        pie_chart_path = os.path.join(static_folder, 'influencers_sponsors_pie_chart.png')
        plt.savefig(pie_chart_path)
        plt.close()
        stats = {
            'total_users': total_users,
            'total_influencers': total_influencers,
            'total_sponsors': total_sponsors,
            'total_campaigns': total_campaigns,
            'total_active_ads': total_active_ads,
            'total_transaction_amount': total_transaction_amount,
            'pie_chart_path': 'influencers_sponsors_pie_chart.png'
        }
        
        return render_template('admin-stats.html', stats=stats)
    return redirect(url_for('index'))


# run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
